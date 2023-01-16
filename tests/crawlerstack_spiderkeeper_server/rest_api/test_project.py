"""Test project"""

from sqlalchemy import func, select

from crawlerstack_spiderkeeper_server.models import Project
from tests.crawlerstack_spiderkeeper_server.rest_api.conftest import \
    assert_status_code


def test_get_multi(client, init_project, api_url):
    """test get_multi"""
    api = api_url + '/projects'
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json().get('data')) == 2
    assert int(response.json().get('total_count')) == 2


def test_get(client, init_project, api_url):
    """test get"""
    api = api_url + '/projects/1'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('id') == 1


def test_create(client, api_url):
    """test create"""
    api = api_url + '/projects'
    data = dict(name="test_01", desc='test_01')
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('name') == data.get('name')


def test_patch(client, init_project, api_url):
    """test patch"""
    api = api_url + '/projects/1'
    data = {'desc': 'test_01'}
    response = client.patch(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('desc') == data.get('desc')


async def test_delete(client, init_project, api_url, session):
    """test delete"""
    api = api_url + '/projects/1'
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(Project))
    assert result == 1
