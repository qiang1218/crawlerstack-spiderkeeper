"""
Test storage api.
"""
import asyncio
import os
import time

import pytest
from furl import furl
from sqlalchemy import select

from crawlerstack_spiderkeeper.db.models import Server, Task, Job
from crawlerstack_spiderkeeper.utils import AppId
from tests.conftest import assert_status_code, build_api_url


def test_create(client, init_task, session):
    """Test create a storage."""
    response = client.get(build_api_url('/tasks'))
    assert_status_code(response)
    assert response.json()
    task = response.json()[0]
    app_id = AppId(task['job_id'], task['id'])
    data = {
        'app_id': str(app_id),
        'data': {'foo': 'bar'}
    }
    response = client.post(build_api_url('/storage'), json=data)
    assert_status_code(response)

    response = client.post(build_api_url(f'/storage/{app_id}/_start'))
    assert_status_code(response)

    time.sleep(1)

    response = client.post(build_api_url(f'/storage/{app_id}/_stop'))
    assert_status_code(response)
    #
    # stmt = select(Server.uri).select_from(Job).join(Server.jobs).where(Job.id == task.job_id)
    # res = await session.scalar(stmt)
    # print(res)
    # file_path = str(furl(server.uri).path)
    # assert os.path.exists(file_path)
    # assert os.path.getsize(file_path)
