"""
Test metric service.
"""
import asyncio

import pytest
from prometheus_client import REGISTRY, generate_latest

from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.services import metric_service
from crawlerstack_spiderkeeper.utils import AppData, AppId


@pytest.mark.asyncio
async def test_start(init_task, session, server_start_signal, caplog):
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
    obj: Task = session.query(Task).first()
    app_data = AppData(AppId(obj.job_id, obj.id), metric_data)
    await metric_service.create(app_data)
    await asyncio.sleep(2)
    txt = generate_latest(REGISTRY).decode()
    assert 'downloader_exception_count' in txt
