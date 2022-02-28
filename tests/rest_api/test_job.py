"""
Test job api
"""
import asyncio

import pytest
from sqlalchemy import select, func

from crawlerstack_spiderkeeper.db.models import Job, Task
from crawlerstack_spiderkeeper.utils.status import Status
from tests.conftest import assert_status_code, build_api_url


def test_get(client, init_job):
    """Test get multi jobs."""
    api = build_api_url('/jobs')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == 2
    assert int(response.headers['X-Total-Count']) == 2


def test_get_by_id(client, init_job):
    """Test get a job."""
    api = build_api_url(f'/jobs/1')
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('id') == 1


@pytest.mark.integration
def test_create(client, init_project, init_server, init_artifact):
    """Test create a job."""
    data = {
        'artifact_id': 1,
        'server_id': 1,
        'name': 'xxx',
        'cmdline': 'python -c "print(10086)"'
    }
    api = build_api_url('/jobs')
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('concurrent') == data.get('concurrent')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete(client, init_job, session):
    """Test delete a job."""
    response = client.delete(build_api_url(f'/jobs/1'))
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(Job))
    assert result == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_job_start(client, init_job, session):
    """Test job start, then stop this job."""
    response = client.post(build_api_url(f'/jobs/1/_run'))
    assert_status_code(response)
    result = await session.scalar(select(func.count()).select_from(Task))
    assert result == 1
