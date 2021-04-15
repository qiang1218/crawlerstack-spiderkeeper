"""
Test storage api.
"""
import asyncio
import os

from furl import furl

from crawlerstack_spiderkeeper.db.models import Server, Task
from crawlerstack_spiderkeeper.utils import AppId
from tests.conftest import assert_status_code, build_api_url


def test_create(client, init_task, session, server_start_signal):
    """Test create a storage."""
    task: Task = session.query(Task).first()
    app_id = AppId(task.job_id, task.id)
    data = {
        'app_id': str(app_id),
        'data': {'foo': 'bar'}
    }
    response = client.post(build_api_url('/storage'), json=data)
    assert_status_code(response)

    response = client.post(build_api_url(f'/storage/{app_id}/_start'))

    assert_status_code(response)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(2))

    response = client.post(build_api_url(f'/storage/{app_id}/_stop'))
    assert_status_code(response)

    server: Server = task.job.server
    file_path = str(furl(server.uri).path)
    assert os.path.exists(file_path)
    assert os.path.getsize(file_path)
