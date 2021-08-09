"""
Test metric service.
"""
import asyncio
import json

import pytest
from prometheus_client import Histogram
from sqlalchemy import select

from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.services import MetricService
from crawlerstack_spiderkeeper.utils import AppData, AppId


@pytest.mark.asyncio
async def test_start(mocker, init_task, session, factory_with_session, caplog):
    """Test start metric task."""
    histogram_mocker = mocker.patch.object(Histogram, 'labels')
    metric_data = {
        'downloader_exception_count': 949135,
    }
    obj = await session.scalar(select(Task))
    app_data = AppData(AppId(obj.job_id, obj.id), metric_data)
    async with factory_with_session(MetricService) as service:
        await service.create(app_data)

    await asyncio.sleep(0.2)
    histogram_mocker.assert_called()
