"""Test job"""
from sqlalchemy import func, select

from crawlerstack_spiderkeeper_server.models import Job
from crawlerstack_spiderkeeper_server.utils.request import RequestWithHttpx
from tests.crawlerstack_spiderkeeper_server.rest_api.conftest import \
    assert_status_code


def test_get_multi(client, init_job, api_url):
    """test get_multi"""
    api = api_url + '/jobs'
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json().get('data')) == 3
    assert int(response.json().get('total_count')) == 3


def test_get(client, init_job, api_url):
    """test get"""
    api = api_url + '/jobs/1'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('id') == 1


def test_create(client, init_artifact, init_storage_server, api_url):
    """test create"""
    api = api_url + '/jobs'
    data = dict(name="test1", trigger_expression="0 0 * * *", storage_enable=True, executor_type='docker',
                storage_server_id=1, artifact_id=1)
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('id') == 1


def test_patch(client, init_job, api_url):
    """test patch"""
    api = api_url + '/jobs/1'
    data = {'trigger_expression': "0 0 1 * *"}
    response = client.patch(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('trigger_expression') == data.get('trigger_expression')


async def test_delete(client, init_job, api_url, session):
    """test delete"""
    api = api_url + '/jobs/1'
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(Job))
    assert result == 2


def test_start(client, init_job, api_url, mocker):
    """test start"""
    api = api_url + '/jobs/1/_start'
    request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'message': 'ok'})
    response = client.get(api)
    assert_status_code(response)
    request.assert_called_once()


def test_pause(client, init_job, api_url, mocker):
    """test pause"""
    api = api_url + '/jobs/2/_pause'
    request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'message': 'ok'})
    response = client.get(api)
    assert_status_code(response)
    request.assert_called_once()


def test_unpause(client, init_job, api_url, mocker):
    """test unpause"""
    api = api_url + '/jobs/3/_unpause'
    request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'message': 'ok'})
    response = client.get(api)
    assert_status_code(response)
    request.assert_called_once()


def test_stop(client, init_job, api_url, mocker):
    """test stop"""
    api = api_url + '/jobs/2/_stop'
    request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'message': 'ok'})
    response = client.get(api)
    assert_status_code(response)
    request.assert_called_once()
