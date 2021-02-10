import asyncio
from datetime import datetime

import pytest
from prometheus_client import REGISTRY, generate_latest

from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.services import metric_service
from crawlerstack_spiderkeeper.utils import AppData, AppId


class TestMetric:

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'except_value',
        [
            datetime.now().second,
            None
        ]
    )
    async def test_start(self, init_task, session, server_start_signal, except_value, caplog):
        obj: Task = session.query(Task).first()
        data = {
            'downloader_request_count': 0,
            'downloader_request_bytes': 0,
            'downloader_request_method_count_GET': 0,
            'downloader_response_count': 0,
            'downloader_response_status_count_200': 0,
            'downloader_response_status_count_301': 0,
            'downloader_response_status_count_302': 0,
            'downloader_response_bytes': 0,
            'downloader_exception_count': except_value,
        }
        app_data = AppData(AppId(obj.job_id, obj.id), data)
        await metric_service.create(app_data)
        await asyncio.sleep(2)
        txt = generate_latest(REGISTRY).decode()
        if except_value:
            assert str(except_value) in txt
        else:
            assert str(except_value) not in txt
            assert 'data parser error.' in caplog.text
