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
from crawlerstack_spiderkeeper.services.metric import MetricBackgroundTask
from crawlerstack_spiderkeeper.utils import AppData, AppId


@pytest.mark.asyncio
async def test_task_start(session, event_loop):
    bg_task = MetricBackgroundTask()
    task = event_loop.create_task(bg_task.start())


@pytest.mark.asyncio
async def test_start(mocker, init_task, session, factory_with_session, caplog):
    """Test start metric task."""
    histogram_mocker = mocker.patch.object(Histogram, 'labels')
    metric_data = {
        'downloader_exception_count': 949135,
    }
    await MetricBackgroundTask.run_from_cls()
    obj = await session.scalar(select(Task))
    app_data = AppData(AppId(obj.job_id, obj.id), metric_data)
    async with factory_with_session(MetricService) as service:
        await service.create(app_data)

    await asyncio.sleep(2)
    await MetricBackgroundTask.stop_from_cls()
    await asyncio.sleep(2)
    # histogram_mocker.assert_called()
