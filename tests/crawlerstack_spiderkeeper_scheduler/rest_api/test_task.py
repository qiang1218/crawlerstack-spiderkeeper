"""Test task"""
from sqlalchemy import select, func

from tests.crawlerstack_spiderkeeper_scheduler.rest_api.conftest import assert_status_code

from crawlerstack_spiderkeeper_scheduler.models import Task
from crawlerstack_spiderkeeper_scheduler.utils.status import Status


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
    assert response.json().get('data').get('name') == '1_scheduler_'


def test_create(client, init_executor, api_url):
    """test create"""
    api = api_url + '/tasks'
    data = dict(name="3_scheduler_", url="http://localhost:2375", type="docker", executor_id=1, status=1,
                container_id='fad343j4er')
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('name') == data.get('name')


def test_patch(client, init_task, api_url):
    """test patch"""
    api = api_url + '/tasks/1'
    data = dict(status=Status.FINISH.value, task_end_time='2022-01-01 01:01:01')
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
