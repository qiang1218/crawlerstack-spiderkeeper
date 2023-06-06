"""test log"""

import pytest
from opentelemetry.sdk._logs import Logger

from crawlerstack_spiderkeeper_server.services import LogService


@pytest.fixture()
def service():
    """service fixture"""
    return LogService()


@pytest.mark.parametrize(
    'data, job_id, task_name, task_time',
    [
        ('test log', '2', '2-scheduled-20191215152202', 20191215152202)
    ]
)
def test_upload_data(service, mocker, data, job_id, task_name, task_time):
    """Test upload data"""
    emit = mocker.patch.object(Logger, 'emit', return_value=None)
    service.upload_data(data, job_id, task_name, task_time)
    emit.assert_called_once()


@pytest.mark.parametrize(
    'data',
    [
        ({'task_name': '2-scheduled-20191215152202',
          'data': ['log1', 'log1']})
    ]
)
async def test_create(service, mocker, data):
    """Test create"""
    upload_data = mocker.patch.object(LogService, 'upload_data', return_value=None)
    await service.create(data)
    upload_data.assert_called()
