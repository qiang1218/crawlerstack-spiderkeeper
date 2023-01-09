"""Test config"""
import logging
import os
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.testclient import TestClient

from fastapi_sa.database import db
from crawlerstack_spiderkeeper_scheduler.manage import SpiderKeeperScheduler
from crawlerstack_spiderkeeper_scheduler.models import BaseModel
from crawlerstack_spiderkeeper_scheduler.config import settings

from crawlerstack_spiderkeeper_scheduler.models import Executor, ExecutorDetail, Task

logger = logging.getLogger(__name__)


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


API_VERSION = 'v1'


@pytest.fixture()
def api_url():
    """build api url"""
    return f'/api/{API_VERSION}'


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
async def spiderkeeper_server(migrate, db_url):
    settings.DATABASE = db_url
    logger.debug('Starting spiderkeeper!!!')
    _spiderkeeper_server = SpiderKeeperScheduler(settings)
    await _spiderkeeper_server.start()
    yield _spiderkeeper_server
    await _spiderkeeper_server.stop()
    logger.debug('Stopping spiderkeeper!!!')


@pytest.fixture()
async def client(spiderkeeper_server):
    """client"""

    _client = TestClient(
        spiderkeeper_server.rest_api.app,
        raise_server_exceptions=False
    )
    yield _client


@pytest.fixture()
async def init_executor():
    """Init executor fixture."""
    async with db():
        executors = [
            Executor(name="docker_executor_1", selector="test", url="http://localhost:2375", type="docker", memory=32,
                     cpu=50),
            Executor(name="docker_executor_2", selector="test", url="http://localhost:2376", type="docker", memory=32,
                     cpu=50),
        ]
        db.session.add_all(executors)
        await db.session.flush()


@pytest.fixture()
async def init_executor_detail(init_executor):
    """Init executor detail fixture."""
    async with db():
        executor_details = [
            ExecutorDetail(task_count=1, executor_id=1),
            ExecutorDetail(task_count=2, executor_id=2),
        ]
        db.session.add_all(executor_details)
        await db.session.flush()


@pytest.fixture()
async def init_task(init_executor):
    """Init task fixture."""
    async with db():
        tasks = [
            Task(name="1_scheduler_", url="http://localhost:2375", type="docker", executor_id=1, status=1,
                 container_id='d343j4er'),
            Task(name="2_scheduler_", url="http://localhost:2375", type="docker", executor_id=1, status=1,
                 container_id='d343j4er'),
        ]
        db.session.add_all(tasks)
        await db.session.flush()
