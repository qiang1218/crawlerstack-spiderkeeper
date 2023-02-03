"""Test config"""
import logging

import pytest
from starlette.testclient import TestClient

from crawlerstack_spiderkeeper_forwarder.config import \
    settings as forwarder_settings
from crawlerstack_spiderkeeper_forwarder.manage import SpiderKeeperForwarder

logger = logging.getLogger(__name__)

API_VERSION = 'v1'


@pytest.fixture()
def api_url():
    """build api url"""
    return f'/api/{API_VERSION}'


@pytest.fixture()
def settings():
    """settings fixture"""
    forwarder_settings.MQ = 'memory://localhost'
    return forwarder_settings


@pytest.fixture(autouse=True)
async def spiderkeeper_executor(settings):
    """spiderkeeper executor fixture"""
    logger.debug('Starting spiderkeeper!!!')
    _spiderkeeper_executor = SpiderKeeperForwarder(settings)
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
