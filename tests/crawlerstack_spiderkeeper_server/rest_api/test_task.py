"""Test task"""

from sqlalchemy import select, func
from tests.crawlerstack_spiderkeeper_server.rest_api.conftest import assert_status_code

from crawlerstack_spiderkeeper_server.models import Task


def test_get_multi(client, init_task, api_url):
    """test get_multi"""
    api = api_url + '/tasks'
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json().get('data')) == 2
    assert int(response.json().get('total_count')) == 2


def test_get(client, init_task, api_url):
    """test get"""
    api = api_url + '/tasks/1'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('id') == 1


def test_create(client, init_job, api_url):
    """test create"""
    api = api_url + '/tasks'
    data = dict(name="test_01", job_id=1)
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('name') == data.get('name')


def test_patch(client, init_task, api_url):
    """test patch"""
    api = api_url + '/tasks/1'
    data = {'status': 1}
    response = client.patch(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('status') == data.get('status')


async def test_delete(client, init_task, api_url, session):
    """test delete"""
    api = api_url + '/tasks/1'
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(Task))
    assert result == 1


def test_get_job_from_task_id(client, init_task, api_url):
    """test get job from task id"""
    api = api_url + '/tasks/1/jobs'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('name') == 'test1'
