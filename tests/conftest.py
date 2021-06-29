"""
Test config.
"""
import os
import tempfile
from datetime import datetime
from shutil import make_archive
from typing import Generator
from urllib.parse import urlparse

import pytest
from aio_pydispatch import Signal
from alembic.command import downgrade as alembic_downgrade
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi import Response, UploadFile
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.db import engine
from crawlerstack_spiderkeeper.db.models import (Artifact, Audit, Job, Project,
                                                 Server, Storage, Task)
from crawlerstack_spiderkeeper.manage import SpiderKeeper
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils.metadata import ArtifactMetadata, Metadata
from crawlerstack_spiderkeeper.utils.states import States


@pytest.fixture()
def temp_dir():
    """
    初始化测试目录，同时将测试目录赋值到 settings 上
    因为测试中所有内容都会放在这个目录，所以在引用 settings 时除非没有引用这个 fixture
    或者使用了这个 fixture 的其他 fixture，否则 settings.ARTIFACT_PATH 都将返回测试目录
    :return:
    """
    with tempfile.TemporaryDirectory(prefix='spiderkeeper-test-') as path:
        settings.ARTIFACT_PATH = path
        yield path


@pytest.fixture()
def base_dir() -> str:
    """Base dir fixture."""
    return os.path.dirname(__file__)


@pytest.fixture()
def data_dir(base_dir):
    """Test data dir fixture."""
    return os.path.join(base_dir, 'data')


@pytest.fixture()
def demo_zip(data_dir, temp_dir) -> Generator[str, None, None]:
    """
    只用 test/data/demo 构建的测试数据
    压缩文件中的目录结构
    xxx-20191215152202.zip
    .
    |-- xxx
    |    |- xxx
    |    |    |- spiders
    |    |    |    |- __init__.py
    |    |    |    └── xxx.py
    |    |    |- settings.py
    |    |    |- middlewares.py
    |    |    └── items.py
    |    |- Dockerfile
    |    |- requirements.txt
    |    |- Pipfile
    |    |- Pipfile.lock
    |    |- setup.py
    |    |- setup.cfg
    |    |- scrapy.cfg
    |    └── README.md
    """
    timestamp = datetime(
        year=2020,
        month=1,
        day=10,
        hour=18,
        minute=30,
        second=20,
        microsecond=262520
    ).timestamp()
    filename = f'demo-{timestamp}.zip'
    base_name, fmt = filename.rsplit('.', 1)
    cwd = os.getcwd()
    metadata = Metadata()
    # 切换目录，将压缩文件保存到该目录
    os.chdir(metadata.artifact_files_path)
    make_archive(
        base_name=base_name,  # 压缩文件前缀名称，不包含压缩后缀格式
        format=fmt,  # 压缩格式，压缩完成后，会自动在文件名上加后缀
        root_dir=os.path.join(data_dir, 'demo'),  # 压缩数据所在目录，压缩文件不包含该目录名称
        # base_dir='demo',    # 要压缩数据的起始目录，压缩文件从该目录开始压缩(包含目录名)。如指定，则压缩 root_dir 下的所有文件。
    )
    # 回到之前目录
    os.chdir(cwd)
    yield os.path.join(metadata.artifact_files_path, filename)


@pytest.fixture(scope='session', name='session_factory')
def session_factory():
    """Session factory fixture"""
    yield sessionmaker(bind=engine, autocommit=True, autoflush=True)


@pytest.fixture(name='uploaded_file')
def fixture_uploaded_file(temp_dir):
    """Uploaded file fixture."""
    with tempfile.NamedTemporaryFile(dir=temp_dir) as file_obj:
        file_obj.write(b'Hello world\n')
        file_obj.seek(0)
        yield UploadFile(file_obj.name, file_obj)


@pytest.fixture()
def migrate():
    """migrate fixture."""
    datetime.now()
    os.chdir(os.path.join(settings.BASE_DIR, 'alembic'))
    alembic_config = AlembicConfig(os.path.join(settings.BASE_DIR, 'alembic', 'alembic.ini'))
    alembic_config.set_main_option('script_location', os.getcwd())
    print(f'\n----- RUN ALEMBIC MIGRATION, DB URI: {settings.DATABASE}\n')
    alembic_downgrade(alembic_config, 'base')
    alembic_upgrade(alembic_config, 'head')
    try:
        yield
    finally:
        alembic_downgrade(alembic_config, 'base')
        try:
            os.remove(urlparse(settings.DATABASE).path)
        except FileNotFoundError:
            pass


@pytest.fixture()
def session(migrate, session_factory) -> Session:
    """Session fixture."""
    _session = session_factory()
    yield _session
    _session.close()


@pytest.fixture()
def init_audit(session):
    """Init audit fixture."""
    with session.begin():
        audits = [
            Audit(
                url='https://example.com',
                method='POST',
                client='127.0.0.1:25552',
                detail='foo'
            ),
            Audit(
                url='https://example.com',
                method='DELETE',
                client='127.0.0.1:27751',
                detail='bar'
            ),
        ]
        session.add_all(audits)
    yield audits


@pytest.fixture()
def init_server(session, temp_dir):
    """Init server fixture."""
    with session.begin():
        servers = [
            Server(name='file', type='file', uri=f'file://{temp_dir}/storage/test.txt'),
            Server(name='redis2', type='redis', uri='redis://localhost'),
        ]
        session.add_all(servers)
    yield servers


@pytest.fixture()
def init_project(session):
    """Init project fixture."""
    with session.begin():
        projects = [
            Project(name="test1", slug="test1"),
            Project(name="test2", slug="test2"),
        ]
        session.add_all(projects)


@pytest.fixture()
async def init_artifact(session, init_project, demo_zip):
    """Init artifact fixture."""
    project = session.query(Project).first()
    with session.begin():
        artifacts = [
            Artifact(project_id=project.id, filename=os.path.basename(demo_zip)),
            Artifact(project_id=project.id, filename=os.path.basename(demo_zip)),
        ]
        session.add_all(artifacts)


@pytest.fixture()
async def init_job(session, init_server, init_artifact):
    """Init job fixture."""
    artifact = session.query(Artifact).first()
    server = session.query(Server).first()
    with session.begin():
        jobs = [
            Job(
                artifact_id=artifact.id, name='1',
                cmdline='python -c "print(123)"',
                server_id=server.id
            ),
            Job(artifact_id=artifact.id, name='2', cmdline='scrapy crawl example'),
        ]
        session.add_all(jobs)


@pytest.fixture()
def init_task(session, init_job):
    """Init task fixture."""
    job = session.query(Job).first()
    with session.begin():
        tasks = [
            Task(job_id=job.id, state=States.RUNNING.value),
            Task(job_id=job.id, state=States.RUNNING.value, container_id='001'),
        ]
        session.add_all(tasks)


@pytest.fixture()
def init_storage(session, init_job):
    """Init storage fixture."""
    obj: Job = session.query(Job).first()
    with session.begin():
        objs = [
            Storage(count=0, state=States.RUNNING.value, job_id=obj.id),
            Storage(count=0, state=States.STOPPED.value, detail='stop...', job_id=obj.id),
        ]
        session.add_all(objs)


def assert_status_code(response: Response, code=200) -> None:
    """Check state code is ok."""
    assert response.status_code == code


API_VERSION = 'v1'


def build_api_url(api: str) -> str:
    """
    # TODO 修改成 fixture，可以避免导入问题
    pass api variable is `/project` not `project`
    :param api:
    :return:
    """
    return f'/api/{API_VERSION}{api}'


@pytest.fixture(name='signal_send')
async def fixture_signal_send():
    """Signal send fixture."""

    async def _(signal: Signal, *args, **kwargs):
        await signal.send(*args, **kwargs)

    yield _


@pytest.fixture(name='server_start_signal')
async def fixture_server_start_signal(signal_send):
    """Server start signal fixture."""
    await signal_send(server_start)
    yield
    await signal_send(server_stop)


@pytest.fixture(name='count_file_factory')
def fixture_count_file_factory():
    """Count file factory fixture."""

    def count_file(path: str):
        """Count file."""
        file_count = 0
        files = os.listdir(path)
        for file in files:
            if os.path.isfile(os.path.join(path, file)):
                file_count += 1
        return file_count

    return count_file


@pytest.fixture(name='artifact_metadata')
def fixture_artifact_metadata(demo_zip):
    """Artifact metadata."""
    yield ArtifactMetadata(os.path.basename(demo_zip))


@pytest.fixture()
def client(migrate):
    """Api client fixture."""
    spider_keeper = SpiderKeeper(settings)
    spider_keeper.api.init()
    _client = TestClient(spider_keeper.api.app, raise_server_exceptions=False)
    yield _client
