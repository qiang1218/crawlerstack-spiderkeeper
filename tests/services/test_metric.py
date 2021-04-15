"""
Test metric service.
"""
import asyncio
from datetime import datetime

import pytest
from prometheus_client import REGISTRY, generate_latest

from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.services import metric_service
from crawlerstack_spiderkeeper.utils import AppData, AppId


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'except_value',
    [
        datetime.now().second,
        None
    ]
)
async def test_start(init_task, session, server_start_signal, metric_data, except_value, caplog):
    """Test start metric task."""
    obj: Task = session.query(Task).first()
    app_data = AppData(AppId(obj.job_id, obj.id), metric_data)
    await metric_service.create(app_data)
    await asyncio.sleep(2)
    txt = generate_latest(REGISTRY).decode()
    if except_value:
        assert str(except_value) in txt
    else:
        assert str(except_value) not in txt
        assert 'data parser error.' in caplog.text
