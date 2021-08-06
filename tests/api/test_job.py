"""
Test job api
"""
import asyncio

import pytest

from crawlerstack_spiderkeeper.db.models import Artifact, Job, Server, Task
from crawlerstack_spiderkeeper.utils.states import States
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
def test_delete(client, init_job):
    """Test delete a job."""
    response = client.delete(build_api_url(f'/jobs/1'))
    assert_status_code(response)
    response = client.get(build_api_url('/jobs'))
    assert int(response.headers['X-Total-Count']) == 1


@pytest.mark.integration
def test_job_start_and_stop(client, init_job):
    """Test job start, then stop this job."""
    response = client.post(build_api_url(f'/jobs/1/_run'))
    assert_status_code(response)
    #
    # resp = client.get(build_api_url('/jobs'))
    # # response = client.post(build_api_url(f'/jobs/1/_stop'))
    # # assert_status_code(response)
    # # response = client.get(build_api_url('/jobs/1/state'))
    # # assert response.json()['state'] == States.STOPPED
