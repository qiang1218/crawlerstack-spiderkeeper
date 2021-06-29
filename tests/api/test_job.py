"""
Test job api
"""
import asyncio

import pytest

from crawlerstack_spiderkeeper.db.models import Artifact, Job, Server, Task
from crawlerstack_spiderkeeper.utils.states import States
from tests.conftest import assert_status_code, build_api_url


def test_get_multi(client, session, init_job):
    """Test get multi jobs."""
    api = build_api_url('/jobs')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == session.query(Job).count()


def test_get(client, session, init_job):
    """Test get a job."""
    obj = session.query(Job).first()
    api = build_api_url(f'/jobs/{obj.id}')
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('id') == obj.id


@pytest.mark.integration
def test_create(client, session, init_project, init_server, init_artifact):
    """Test create a job."""
    obj = session.query(Artifact).first()
    data = {
        'artifact_id': obj.id,
        'server_id': session.query(Server).first().id,
        'name': 'xxx',
        'cmdline': 'python -c "print(10086)"'
    }
    api = build_api_url('/jobs')
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('concurrent') == data.get('concurrent')


@pytest.mark.integration
def test_delete(client, init_job, session):
    """Test delete a job."""
    obj: Job = session.query(Job).first()
    count = session.query(Job).count()
    response = client.delete(build_api_url(f'/jobs/{obj.id}'))
    assert_status_code(response)
    assert session.query(Job).count() == count - 1


@pytest.mark.integration
def test_job_start_and_stop(client, init_job, session):
    """Test job start, then stop this job."""
    obj: Job = session.query(Job).first()
    response = client.post(build_api_url(f'/jobs/{obj.id}/_run'))
    assert_status_code(response)

    asyncio.run(asyncio.sleep(2))

    response = client.post(build_api_url(f'/jobs/{obj.id}/_stop'))
    assert_status_code(response)
    assert session.query(Task).count() == 1
    task: Task = session.query(Task).first()
    assert task.state == States.STOPPED
