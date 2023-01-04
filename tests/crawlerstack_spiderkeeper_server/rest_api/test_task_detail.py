"""Test task detail"""

from sqlalchemy import select, func
from tests.crawlerstack_spiderkeeper_server.rest_api.conftest import assert_status_code

from crawlerstack_spiderkeeper_server.models import TaskDetail


def test_get_multi(client, init_task_detail, api_url):
    """test get_multi"""
    api = api_url + '/task_details'
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json().get('data')) == 2
    assert int(response.json().get('total_count')) == 2


def test_get(client, init_task_detail, api_url):
    """test get"""
    api = api_url + '/task_details/1'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('id') == 1


def test_create(client, init_task, api_url):
    """test create"""
    api = api_url + '/task_details'
    data = dict(task_id=1, item_count=2)
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('item_count') == data.get('item_count')


def test_patch(client, init_task_detail, api_url):
    """test patch"""
    api = api_url + '/task_details/1'
    data = {'item_count': 5}
    response = client.patch(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('item_count') == data.get('item_count')


async def test_delete(client, init_task_detail, api_url, session):
    """test delete"""
    api = api_url + '/task_details/1'
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(TaskDetail))
    assert result == 1


async def test_get_task_from_task_id(client, init_task_detail, api_url):
    """test get task from task id"""
    api = api_url + '/task_details/1/tasks'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('name') == 'test1'
