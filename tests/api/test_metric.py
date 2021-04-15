"""
Test metric api.
"""
import asyncio

from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.utils import AppId
from tests.conftest import assert_status_code, build_api_url


def test_metric(init_task, session, client, server_start_signal, metric_data):
    """Test metric."""
    task: Task = session.query(Task).first()

    data = {
        'app_id': str(AppId(task.job_id, task.id)),
        'data': metric_data
    }
    metric_create_api = build_api_url('/metric')
    metric_creat_response = client.post(metric_create_api, json=data)
    assert_status_code(metric_creat_response)
    asyncio.run(asyncio.sleep(2))
    metric_response = client.get('/metrics')
    assert_status_code(metric_response)
    assert '10086' in metric_response.text
