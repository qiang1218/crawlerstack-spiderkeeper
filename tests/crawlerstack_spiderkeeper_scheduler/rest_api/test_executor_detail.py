"""Test executor detail"""
from sqlalchemy import select, func

from tests.crawlerstack_spiderkeeper_scheduler.rest_api.conftest import assert_status_code

from crawlerstack_spiderkeeper_scheduler.models import ExecutorDetail


def test_get_multi(client, init_executor_detail, api_url):
    """test get_multi"""
    api = api_url + '/executor_details'
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json().get('data')) == 2
    assert int(response.json().get('total_count')) == 2


def test_get(client, init_executor_detail, api_url):
    """test get"""
    api = api_url + '/executor_details/1'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('id') == 1


def test_create(client, api_url):
    """test create"""
    api = api_url + '/executor_details'
    data = dict(task_count=2, executor_id=1)
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('task_count') == data.get('task_count')


def test_patch(client, init_executor_detail, api_url):
    """test patch"""
    api = api_url + '/executor_details/1'
    data = {'task_count': 5}
    response = client.patch(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('task_count') == data.get('task_count')


async def test_delete(client, init_executor_detail, api_url, session):
    """test delete"""
    api = api_url + '/executor_details/1'
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(ExecutorDetail))
    assert result == 1
