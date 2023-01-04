"""Test config"""
import logging
import os
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.testclient import TestClient

from fastapi_sa.database import db
from crawlerstack_spiderkeeper_server.manage import SpiderKeeperServer
from crawlerstack_spiderkeeper_server.models import BaseModel
from crawlerstack_spiderkeeper_server.config import settings as server_settings

logger = logging.getLogger(__name__)


@pytest.fixture()
def settings():
    server_settings.EXPIRE_INTERVAL = 0.5
    return server_settings


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


# @pytest.fixture(autouse=True)
async def spiderkeeper_server(migrate, db_url, settings):
    settings.DATABASE = db_url
    logger.debug('Starting spiderkeeper!!!')
    _spiderkeeper_server = SpiderKeeperServer(settings)
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
