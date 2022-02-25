"""
Test config.
"""
import contextlib
import logging
import os
import tempfile
from datetime import datetime
from shutil import make_archive
from typing import AsyncContextManager, Callable, Generator, TypeVar

import pytest

from fastapi import Response, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.db.models import (Artifact, Audit, Job, Project,
                                                 Server, Storage, Task, BaseModel)
from crawlerstack_spiderkeeper.manage import SpiderKeeper
from crawlerstack_spiderkeeper.utils.metadata import ArtifactMetadata, Metadata
from crawlerstack_spiderkeeper.utils.status import Status

logger = logging.getLogger(__name__)

_T = TypeVar('_T')


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


@pytest.fixture(name='uploaded_file')
def fixture_uploaded_file(temp_dir):
    """Uploaded file fixture."""
    with tempfile.NamedTemporaryFile(dir=temp_dir) as file_obj:
        file_obj.write(b'Hello world\n')
        file_obj.seek(0)
        yield UploadFile(file_obj.name, file_obj)


@pytest.fixture()
async def engine():
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE,
        # echo=True,
    )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture()
async def session_factory(engine):
    """Session factory fixture"""
    yield sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=True,
        autocommit=False,
        expire_on_commit=False,
    )


@pytest.fixture()
async def migrate(engine):
    """migrate fixture."""
    # datetime.now()
    # os.chdir(os.path.join(settings.BASE_DIR, 'alembic'))
    # alembic_config = AlembicConfig(os.path.join(settings.BASE_DIR, 'alembic', 'alembic.ini'))
    # alembic_config.set_main_option('script_location', os.getcwd())
    # logging.error(f'\x1b[1m----- RUN ALEMBIC MIGRATION, DB URI: "{settings.DATABASE}". -----\n\x1b[0m')
    # alembic_downgrade(alembic_config, 'base')
    # alembic_upgrade(alembic_config, 'head')
    # try:
    #     yield
    # finally:
    #     alembic_downgrade(alembic_config, 'base')
    #     try:
    #         os.remove(urlparse(settings.DATABASE).path)
    #     except FileNotFoundError:
    #         pass
    # logging.error(f'\x1b[1m----- CLEANUP ALEMBIC MIGRATION FINISHED. -----\n\x1b[0m')

    logger.info('Creating all tables to database.')
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)
    yield


@pytest.fixture()
async def session(migrate, session_factory) -> AsyncSession:
    """Session fixture."""
    async with session_factory() as _session:
        yield _session


@pytest.fixture()
async def init_audit(session):
    """Init audit fixture."""
    async with session.begin():
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
    return audits


@pytest.fixture()
async def init_server(session, temp_dir):
    """Init server fixture."""
    async with session.begin():
        servers = [
            Server(name='file', type='file', uri=f'file://{temp_dir}/storage/test.txt'),
            Server(name='redis2', type='redis', uri='redis://localhost'),
        ]
        session.add_all(servers)
    return servers


@pytest.fixture()
async def init_project(session) -> list[Project]:
    """Init project fixture."""
    async with session.begin():
        projects = [
            Project(name="test1", slug="test1"),
            Project(name="test2", slug="test2"),
        ]
        session.add_all(projects)
    return projects


@pytest.fixture()
async def init_artifact(session, init_project, demo_zip):
    """Init artifact fixture."""
    async with session.begin():
        project = await session.scalar(select(Project))
        artifacts = [
            Artifact(project_id=project.id, filename=os.path.basename(demo_zip)),
            Artifact(project_id=project.id, filename=os.path.basename(demo_zip)),
        ]
        session.add_all(artifacts)
    return artifacts


@pytest.fixture()
async def init_job(session, init_server, init_artifact):
    """Init job fixture."""
    async with session.begin():
        artifact = await session.scalar(select(Artifact))
        server = await session.scalar(select(Server))
        jobs = [
            Job(
                artifact_id=artifact.id, name='1',
                cmdline='python -c "print(123)"',
                server_id=server.id
            ),
            Job(artifact_id=artifact.id, name='2', cmdline='scrapy crawl example'),
        ]
        session.add_all(jobs)
    return jobs


@pytest.fixture()
async def init_task(session, init_job) -> list[Task]:
    """Init task fixture."""
    async with session.begin():
        job = await session.scalar(select(Job))
        tasks = [
            Task(job_id=job.id, status=Status.RUNNING.value),
            Task(job_id=job.id, status=Status.RUNNING.value, container_id='001'),
        ]
        session.add_all(tasks)
    return tasks


@pytest.fixture()
async def init_storage(session, init_job):
    """Init storage fixture."""
    async with session.begin():
        obj: Job = await session.scalar(select(Job))
        objs = [
            Storage(count=0, status=Status.RUNNING.value, job_id=obj.id),
            Storage(count=0, status=Status.STOPPED.value, detail='stop...', job_id=obj.id),
        ]
        session.add_all(objs)
    return obj


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


@pytest.fixture(autouse=True)
async def spiderkeeper(migrate):
    _spiderkeeper = SpiderKeeper(settings)
    logger.debug('Starting spiderkeeper!!!')
    await _spiderkeeper.start()
    yield _spiderkeeper
    await _spiderkeeper.stop()
    logger.debug('Stopped spiderkeeper!!!')


@pytest.fixture()
async def client(spiderkeeper):
    """Api client fixture."""
    _client = TestClient(
        spiderkeeper.rest_api.app,
        # raise_server_exceptions=False
    )
    yield _client


@pytest.fixture()
def factory_with_session(spiderkeeper) -> Callable[..., AsyncContextManager[_T]]:
    @contextlib.asynccontextmanager
    async def factory(kls: _T):
        async with spiderkeeper.db.session() as session:
            async with session.begin():
                yield kls(session)

    return factory
