"""Test config"""
import logging
import os
import tempfile
from pathlib import Path

import pytest
from fastapi_sa.database import db
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.testclient import TestClient

from crawlerstack_spiderkeeper_server.config import settings as server_settings
from crawlerstack_spiderkeeper_server.manage import SpiderKeeperServer
from crawlerstack_spiderkeeper_server.models import (Artifact, BaseModel, Job,
                                                     Project, StorageServer,
                                                     Task, TaskDetail)

logger = logging.getLogger(__name__)


@pytest.fixture()
def settings():
    server_settings.EXPIRE_INTERVAL = 0.5
    return server_settings


@pytest.fixture()
def temp_dir():
    """
    初始化测试目录，同时将测试目录赋值到 settings 上
    因为测试中所有内容都会放在这个目录，所以在引用 settings 时除非没有引用这个 fixture
    或者使用了这个 fixture 的其他 fixture，否则 settings.ARTIFACT_PATH 都将返回测试目录
    :return:
    """
    with tempfile.TemporaryDirectory(prefix='spiderkeeper-test-') as path:
        yield Path(path)


@pytest.fixture()
def demo_file(temp_dir):
    """Fixture demo file"""
    with tempfile.NamedTemporaryFile(
            mode='w',
            prefix='test-tail',
            suffix='.txt',
            dir=temp_dir,
            newline=os.linesep,  # Windows `\r\n`  unix `\r\n`
            delete=False
    ) as file:
        file.write("""MIT License

Copyright (c) <YEAR> <COPYRIGHT HOLDER>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")
        file.flush()
        name = Path(file.name)
    # Windows 如果打开要给已经打开的文件，会报错，这里将临时文件的 delete=False
    # 临时目录会自动删除该目录下的文件。
    yield name


@pytest.fixture()
def demo_create_file(temp_dir):
    """Fixture demo file"""
    with tempfile.NamedTemporaryFile(
            mode='w',
            prefix='test-tail',
            suffix='.txt',
            dir=temp_dir,
            newline=os.linesep,  # Windows `\r\n`  unix `\r\n`
            delete=False
    ) as file:
        name = Path(file.name)
    # Windows 如果打开要给已经打开的文件，会报错，这里将临时文件的 delete=False
    # 临时目录会自动删除该目录下的文件。
    yield name


@pytest.fixture()
def db_url():
    """db url"""
    return "sqlite+aiosqlite:////tmp/test.db"


@pytest.fixture()
def db_session_ctx():
    """db session context"""
    token = db.set_session_ctx()
    yield
    db.reset_session_ctx(token)


@pytest.fixture()
async def session(db_session_ctx):
    """session fixture"""
    async with db.session.begin():
        yield db.session


@pytest.fixture(autouse=True)
async def migrate(db_url):
    """migrate fixture"""
    os.makedirs(Path(db_url.split('///')[1]).parent, exist_ok=True)
    _engine = create_async_engine(db_url)
    async with _engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)
    await _engine.dispose()


@pytest.fixture(autouse=True)
async def spiderkeeper_server(migrate, db_url, settings):
    settings.DATABASE = db_url
    logger.debug('Starting spiderkeeper!!!')
    _spiderkeeper_server = SpiderKeeperServer(settings)
    await _spiderkeeper_server.start()
    yield _spiderkeeper_server
    await _spiderkeeper_server.stop()
    logger.debug('Stopping spiderkeeper!!!')


API_VERSION = 'v1'


@pytest.fixture()
def api_url():
    """build api url"""
    return f'/api/{API_VERSION}'


@pytest.fixture()
async def client(spiderkeeper_server):
    """client"""

    _client = TestClient(
        spiderkeeper_server.rest_api.app,
        raise_server_exceptions=False
    )
    yield _client


@pytest.fixture()
async def init_project():
    """Init project fixture."""
    async with db():
        projects = [
            Project(name="test1", desc="test1"),
            Project(name="test2", desc="test2"),
        ]
        db.session.add_all(projects)
        await db.session.flush()


@pytest.fixture()
async def init_artifact(init_project):
    """Init artifact fixture."""
    async with db():
        artifacts = [
            Artifact(name="test1", desc="test1", image='test1', version='latest', project_id=1),
            Artifact(name="test2", desc="test2", image='test2', version='latest', project_id=2),
        ]
        db.session.add_all(artifacts)
        await db.session.flush()


@pytest.fixture()
async def init_storage_server():
    """Init storage server fixture."""
    async with db():
        storage_servers = [
            StorageServer(name="test1", url="mysql://root:root@localhost:3306/spiderkeeper_server",
                          storage_class='mysql'),
            StorageServer(name="test2", url="mysql://root:root@localhost:3306/spiderkeeper_server",
                          storage_class='mysql'),
        ]
        db.session.add_all(storage_servers)
        await db.session.flush()


@pytest.fixture()
async def init_job(init_artifact, init_storage_server):
    """Init job fixture."""
    async with db():
        jobs = [
            Job(name="test1", trigger_expression="0 0 * * *", storage_enable=True, executor_type='docker',
                storage_server_id=1, artifact_id=1, enabled=False, pause=False),
            Job(name="test2", trigger_expression="0 1 * * *", storage_enable=False, executor_type='docker',
                artifact_id=1, enabled=True, pause=False),
            Job(name="test3", trigger_expression="0 1 * * *", storage_enable=False, executor_type='docker',
                artifact_id=1, enabled=True, pause=True),
        ]
        db.session.add_all(jobs)
        await db.session.flush()


@pytest.fixture()
async def init_task(init_job):
    """Init task fixture."""
    async with db():
        tasks = [
            Task(name="test1", job_id=1),
            Task(name="test2", job_id=2),
        ]
        db.session.add_all(tasks)
        await db.session.flush()


@pytest.fixture()
async def init_task_detail(init_task):
    """Init task detail fixture."""
    async with db():
        task_details = [
            TaskDetail(item_count=0, task_id=1),
            TaskDetail(item_count=1, task_id=2),
        ]
        db.session.add_all(task_details)
        await db.session.flush()
