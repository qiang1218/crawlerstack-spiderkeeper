"""
Test metric service.
"""
import asyncio

import pytest
from prometheus_client import REGISTRY, generate_latest
from sqlalchemy import select

from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.services import MetricService
from crawlerstack_spiderkeeper.utils import AppData, AppId


@pytest.mark.asyncio
async def test_start(init_task, session, server_start_signal, factory_with_session, caplog):
    """Test start metric task."""
    metric_data = {
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
    obj = await session.scalar(select(Task))
    app_data = AppData(AppId(obj.job_id, obj.id), metric_data)
    async with factory_with_session(MetricService) as service:
        await service.create_msg(app_data)

    await asyncio.sleep(0.1)
    txt = generate_latest(REGISTRY).decode()
    assert 'downloader_exception_count' in txt
