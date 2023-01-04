"""Test storage server"""

from sqlalchemy import select, func
from tests.crawlerstack_spiderkeeper_server.rest_api.conftest import assert_status_code

from crawlerstack_spiderkeeper_server.models import StorageServer


def test_get_multi(client, init_storage_server, api_url):
    """test get_multi"""
    api = api_url + '/storage_servers'
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json().get('data')) == 2
    assert int(response.json().get('total_count')) == 2


def test_get(client, init_storage_server, api_url):
    """test get"""
    api = api_url + '/storage_servers/1'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('id') == 1


def test_create(client, api_url):
    """test create"""
    api = api_url + '/storage_servers'
    data = dict(name="test1", url="mysql://root:root@localhost:3306/spiderkeeper_server",
                storage_class='mysql')
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('name') == data.get('name')


def test_patch(client, init_storage_server, api_url):
    """test patch"""
    api = api_url + '/storage_servers/1'
    data = {'name': 'test_01'}
    response = client.patch(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('desc') == data.get('desc')


async def test_delete(client, init_storage_server, api_url, session):
    """test delete"""
    api = api_url + '/storage_servers/1'
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(StorageServer))
    assert result == 1
