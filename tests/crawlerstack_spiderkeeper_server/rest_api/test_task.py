"""Test task"""

from sqlalchemy import func, select

from crawlerstack_spiderkeeper_server.models import Task
from crawlerstack_spiderkeeper_server.services import TaskService
from crawlerstack_spiderkeeper_server.signals import data_task_start
from tests.crawlerstack_spiderkeeper_server.rest_api.conftest import \
    assert_status_code


def test_get_multi(client, init_task, api_url):
    """Test get_multi"""
    api = api_url + '/tasks'
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json().get('data')) == 2
    assert int(response.json().get('total_count')) == 2


def test_get(client, init_task, api_url):
    """Test get"""
    api = api_url + '/tasks/1'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('id') == 1


def test_create(client, init_job, api_url, mocker):
    """Test create"""
    api = api_url + '/tasks'
    data = dict(name="test_01", job_id=1)
    mocker.patch.object(data_task_start, 'send')
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('name') == data.get('name')


def test_patch(client, init_task, api_url):
    """Test patch"""
    api = api_url + '/tasks/1'
    data = {'task_status': 1}
    response = client.patch(api, json=data)
    assert_status_code(response)
    assert response.json().get('data').get('task_status') == data.get('task_status')


async def test_delete(client, init_task, api_url, session):
    """Test delete"""
    api = api_url + '/tasks/1'
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(Task))
    assert result == 1


def test_get_job_from_task_id(client, init_task, api_url):
    """Test get job from task id"""
    api = api_url + '/tasks/1/jobs'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('name') == 'test1'


def test_start_task_consume(client, init_task, api_url, mocker):
    """Test start task consume"""
    api = api_url + '/tasks/1/_start'
    mocker.patch.object(TaskService, 'start_task_consume', return_value='ok')
    response = client.get(api)
    assert_status_code(response)


def test_stop_task_consume(client, init_task, api_url, mocker):
    """Test stop task consume"""
    api = api_url + '/tasks/1/_stop'
    mocker.patch.object(TaskService, 'stop_task_consume', return_value='ok')
    response = client.get(api)
    assert_status_code(response)


def test_terminate_task_consume(client, init_task, api_url, mocker):
    """Test terminate task consume"""
    api = api_url + '/tasks/1/_terminate'
    mocker.patch.object(TaskService, 'terminate_task_consume', return_value='ok')
    response = client.get(api)
    assert_status_code(response)
