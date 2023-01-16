"""test metric"""

import asyncio

import pytest

from crawlerstack_spiderkeeper_server.services.metric import MetricService
from tests.crawlerstack_spiderkeeper_server.rest_api.conftest import \
    assert_status_code


@pytest.fixture
def metric_service():
    """metric service fixture"""
    return MetricService()


def test_metric(client, metric_service):
    """test metric."""
    metric_service.set_metric('2-scheduled-20191215152202', {'downloader_request_count': 10086})
    asyncio.run(asyncio.sleep(2))

    metric_response = client.get('/metrics')
    assert_status_code(metric_response)
    assert '10086' in metric_response.text
