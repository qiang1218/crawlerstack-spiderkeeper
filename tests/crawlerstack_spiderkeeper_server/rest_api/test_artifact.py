"""Test artifact"""

from sqlalchemy import select, func
from tests.crawlerstack_spiderkeeper_server.rest_api.conftest import assert_status_code

from crawlerstack_spiderkeeper_server.models import Artifact


def test_get_multi(client, init_artifact, api_url):
    """test get_multi"""
    api = api_url + '/artifacts'
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json().get('data')) == 2
    assert int(response.json().get('total_count')) == 2


def test_get(client, init_artifact, api_url):
    """test get"""
    api = api_url + '/artifacts/1'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('id') == 1


def test_create(client, init_project, api_url):
    """test create"""
    api = api_url + '/artifacts'
    data = dict(name="test1", desc="test1", image='test1', project_id=1)
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('name') == data.get('name')


def test_patch(client, init_artifact, api_url):
    """test patch"""
    api = api_url + '/artifacts/1'
    data = {'desc': 'test_01'}
    response = client.patch(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('desc') == data.get('desc')


async def test_delete(client, init_artifact, api_url, session):
    """test delete"""
    api = api_url + '/artifacts/1'
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(Artifact))
    assert result == 1
