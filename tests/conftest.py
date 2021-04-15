"""
Test config.
"""
import asyncio
import io
import os
import tempfile
from datetime import datetime
from shutil import make_archive
from unittest.mock import MagicMock
from urllib.parse import urlparse

import pytest
from aio_pydispatch import Signal
from aiodocker.utils import mktar_from_dockerfile
from alembic.command import downgrade as alembic_downgrade
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy.orm import Session, sessionmaker
from starlette.datastructures import UploadFile
from starlette.responses import Response
from starlette.testclient import TestClient

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.db import SessionFactory, engine
from crawlerstack_spiderkeeper.db.models import (Artifact, Audit, Job, Project,
                                                 Server, Storage, Task)
from crawlerstack_spiderkeeper.manage import SpiderKeeper
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils.metadata import ArtifactMetadata, Metadata
from crawlerstack_spiderkeeper.utils.states import States

API_VERSION = 'v1'


def assert_status_code(response: Response, code=200) -> None:
    """Check state code is ok."""
    assert response.status_code == code


def build_api_url(api: str) -> str:
    """
    # TODO 修改成 fixture，可以避免导入问题
    pass api variable is `/project` not `project`
    :param api:
    :return:
    """
    return f'/api/{API_VERSION}{api}'


@pytest.fixture(name='url_builder')
def fixture_url_builder():
    """Url builder."""

    def _(*args):
        url_segment = ['/api', API_VERSION]
        for segment in args:
            url_segment.append(segment.lstrip('/'))
        return '/'.join(url_segment)

    return _


@pytest.fixture(name='temp_dir')
def fixture_temp_dir():
    """
    初始化测试目录，同时将测试目录赋值到 settings 上
    因为测试中所有内容都会放在这个目录，所以在引用 settings 时除非没有引用这个 fixture
    或者使用了这个 fixture 的其他 fixture，否则 settings.ARTIFACT_PATH 都将返回测试目录
    :return:
    """
    path = tempfile.TemporaryDirectory(prefix='spiderkeeper-test-')
    settings.ARTIFACT_PATH = path.name
    try:
        yield path.name
    finally:
        path.cleanup()


@pytest.fixture(name='base_dir')
def fixture_base_dir() -> str:
    """Base dir fixture."""
    return os.path.dirname(__file__)


@pytest.fixture(name='test_data_dir')
def fixture_test_data_dir(base_dir):
    """Test data dir fixture."""
    return os.path.join(base_dir, 'data')


@pytest.fixture(name='demo_zip')
def fixture_demo_zip(test_data_dir, temp_dir) -> str:
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


    :param test_data_dir:
    :param temp_dir:
    :return:
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
        root_dir=os.path.join(test_data_dir, 'demo'),  # 压缩数据所在目录，压缩文件不包含该目录名称
        # base_dir='demo',    # 要压缩数据的起始目录，压缩文件从该目录开始压缩(包含目录名)。如指定，则压缩 root_dir 下的所有文件。
    )
    # 回到之前目录
    os.chdir(cwd)
    yield os.path.join(metadata.artifact_files_path, filename)


@pytest.fixture(name='artifact_metadata')
def fixture_artifact_metadata(demo_zip):
    """Artifact metadata."""
    yield ArtifactMetadata(os.path.basename(demo_zip))


@pytest.fixture(name='uploaded_file')
def fixture_uploaded_file(temp_dir):
    """Uploaded file fixture."""
    file_obj = tempfile.NamedTemporaryFile(dir=temp_dir)
    file_obj.write(b'Hello world\n')
    file_obj.seek(0)
    yield UploadFile(file_obj.name, file_obj)
    file_obj.close()


@pytest.fixture(name='docker_tar_file')
async def fixture_docker_tar_file():
    """
    Mock docker tar file
    :return:
    """

    docker_file = (
        'FROM python'
    )

    docker_file_obj = io.BytesIO(docker_file.encode('utf-8'))
    return mktar_from_dockerfile(docker_file_obj)


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


@pytest.fixture(name='event_loop')
def fixture_event_loop():
    """Event loop fixture."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.call_soon(loop.close)
    if loop.is_running():
        loop.close()


@pytest.fixture(name='metric_data')
def fixture_metric_data():
    """Metric data"""
    yield {
        'downloader_request_count': 0,
        'downloader_request_bytes': 0,
        'downloader_request_method_count_GET': 0,
        'downloader_response_count': 0,
        'downloader_response_status_count_200': 0,
        'downloader_response_status_count_301': 0,
        'downloader_response_status_count_302': 0,
        'downloader_response_bytes': 0,
        'downloader_exception_count': 10086,
    }


class AsyncMock(MagicMock):
    """
    AsyncMock
    ref: https://stackoverflow.com/a/32498408/11722440

    Usage:

    ```
    mocker.patch.object(foo, 'bar', new_callable=AsyncMock)
    ```
    """

    async def __call__(self, *args, **kwargs):  # pylint: disable=invalid-overridden-method, useless-super-delegation
        return super().__call__(*args, **kwargs)

    def __await__(self):
        return self


@pytest.fixture(name='migrate')
def fixture_migrate():
    """migrate fixture."""
    datetime.now()
    os.chdir(os.path.join(settings.BASE_DIR, 'alembic'))
    alembic_config = AlembicConfig(os.path.join(settings.BASE_DIR, 'alembic', 'alembic.ini'))
    # uri = get_db_uri(settings)
    # alembic_config.set_main_option('sqlalchemy.url', uri)
    alembic_config.set_main_option('script_location', os.getcwd())
    print('\n----- RUN ALEMBIC MIGRATION, DB URI: \n')
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


@pytest.fixture(scope='session', name='session_factory')
def fixture_session_factory():
    """Session factory fixture"""
    yield sessionmaker(bind=engine, autocommit=True, autoflush=True)


@pytest.fixture(name='session')
def fixture_session(migrate, session_factory) -> Session:
    """Session fixture."""
    session = session_factory()
    yield session
    session.close()


@pytest.fixture(name='client')
def fixture_client(migrate):
    """Api client fixture."""
    spider_keeper = SpiderKeeper(settings)
    spider_keeper.api.init()
    client = TestClient(spider_keeper.api.app, raise_server_exceptions=False)
    yield client


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


@pytest.fixture(name='init_audit')
def fixture_init_audit(migrate):
    """Init audit fixture."""
    session = SessionFactory()
    audits = [
        Audit(url='http://example.com', method='POST', client='127.0.0.1:25552', detail='foo'),
        Audit(url='http://example.com', method='DELETE', client='127.0.0.1:27751', detail='bar'),
    ]
    session.add_all(audits)
    session.commit()
    yield audits


@pytest.fixture(name='init_server')
def fixture_init_server(migrate, temp_dir):
    """Init server fixture."""
    session = SessionFactory()
    servers = [
        Server(name='file', type='file', uri=f'file://{temp_dir}/storage/test.txt'),
        Server(name='redis2', type='redis', uri='redis://localhost'),
    ]
    session.add_all(servers)
    session.commit()
    session.close()


@pytest.fixture(name='init_project')
def fixture_init_project(migrate):
    """Init project fixture."""
    session = SessionFactory()
    projects = [
        Project(name="test1", slug="test1"),
        Project(name="test2", slug="test2"),
    ]
    session.add_all(projects)
    session.commit()
    session.close()


@pytest.fixture(name='init_artifact')
async def fixture_init_artifact(init_project, demo_zip):
    """Init artifact fixture."""
    session = SessionFactory()
    project = session.query(Project).first()
    artifacts = [
        Artifact(project_id=project.id, filename=os.path.basename(demo_zip)),
        Artifact(project_id=project.id, filename=os.path.basename(demo_zip)),
    ]
    session.add_all(artifacts)
    session.commit()
    session.close()


@pytest.fixture(name='init_job')
async def fixture_init_job(init_server, init_artifact):
    """Init job fixture."""
    session = SessionFactory()
    artifact = session.query(Artifact).first()
    server = session.query(Server).first()
    jobs = [
        Job(
            artifact_id=artifact.id, name='1',
            cmdline='python -c "print(123)"',
            server_id=server.id
        ),
        Job(artifact_id=artifact.id, name='2', cmdline='scrapy crawl example'),
    ]
    session.add_all(jobs)
    session.commit()
    session.close()


@pytest.fixture(name='init_task')
def fixture_init_task(init_job):
    """Init task fixture."""
    session = SessionFactory()
    job = session.query(Job).first()
    tasks = [
        Task(job_id=job.id, state=States.RUNNING.value),
        Task(job_id=job.id, state=States.RUNNING.value, container_id='001'),
    ]
    session.add_all(tasks)
    session.commit()
    session.close()


@pytest.fixture(name='init_storage')
def fixture_init_storage(init_job):
    """Init storage fixture."""
    session = SessionFactory()
    obj: Job = session.query(Job).first()
    objs = [
        Storage(count=0, state=States.RUNNING.value, job_id=obj.id),
        Storage(count=0, state=States.STOPPED.value, detail='stop...', job_id=obj.id),
    ]
    session.add_all(objs)
    session.commit()
    session.close()
