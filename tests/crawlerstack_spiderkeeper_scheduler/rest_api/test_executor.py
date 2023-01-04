"""Test executor"""
from sqlalchemy import select, func

from tests.crawlerstack_spiderkeeper_scheduler.rest_api.conftest import assert_status_code

from crawlerstack_spiderkeeper_scheduler.models import Executor


def test_get_multi(client, init_executor, api_url):
    """test get_multi"""
    api = api_url + '/executors'
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json().get('data')) == 2
    assert int(response.json().get('total_count')) == 2


def test_get(client, init_executor, api_url):
    """test get"""
    api = api_url + '/executors/1'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('id') == 1


def test_create(client, api_url):
    """test create"""
    api = api_url + '/executors'
    data = dict(name="docker_executor_1", selector="test", url="http://localhost:2375", type="docker", memory=32,
                cpu=50)
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('name') == data.get('name')


def test_patch(client, init_executor, api_url):
    """test patch"""
    api = api_url + '/executors/1'
    data = {'memory': 16, 'cpu': 60}
    response = client.patch(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('memory') == data.get('memory')


async def test_delete(client, init_executor, api_url, session):
    """test delete"""
    api = api_url + '/executors/1'
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(Executor))
    assert result == 1
