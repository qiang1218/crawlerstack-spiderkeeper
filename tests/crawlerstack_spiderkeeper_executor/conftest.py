"""Test config"""
import logging

import pytest
from starlette.testclient import TestClient

from crawlerstack_spiderkeeper_executor.config import \
    settings as executor_settings
from crawlerstack_spiderkeeper_executor.manage import SpiderKeeperExecutor

logger = logging.getLogger(__name__)

API_VERSION = 'v1'


@pytest.fixture()
def api_url():
    """build api url"""
    return f'/api/{API_VERSION}'


@pytest.fixture()
def settings():
    """settings fixture"""
    executor_settings.HEARTBEAT_TIMEOUT = 5
    executor_settings.HEARTBEAT_INTERVAL = 3
    executor_settings.EXECUTOR_REMOTE_URL = 'tcp://192.168.186.128:2376'
    return executor_settings


@pytest.fixture(autouse=True)
async def spiderkeeper_executor(settings):
    """spiderkeeper executor fixture"""
    logger.debug('Starting spiderkeeper!!!')
    _spiderkeeper_executor = SpiderKeeperExecutor(settings)
    await _spiderkeeper_executor.start()
    yield _spiderkeeper_executor
    await _spiderkeeper_executor.stop()
    logger.debug('Stopping spiderkeeper!!!')


@pytest.fixture()
async def client(spiderkeeper_executor):
    """client"""

    _client = TestClient(
        spiderkeeper_executor.rest_api.app,
        raise_server_exceptions=False
    )
    yield _client
