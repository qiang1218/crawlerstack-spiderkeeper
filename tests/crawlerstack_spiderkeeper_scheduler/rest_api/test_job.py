"""test job"""

from crawlerstack_spiderkeeper_scheduler.services import JobService
from tests.crawlerstack_spiderkeeper_scheduler.rest_api.conftest import \
    assert_status_code


def test_start(client, api_url, mocker):
    """test start"""
    api = api_url + '/jobs/1/_start'
    mock_method = mocker.patch.object(JobService, 'start_by_id')
    response = client.get(api)
    assert_status_code(response)
    assert mock_method.called


def test_stop(client, api_url, mocker):
    """test stop"""
    api = api_url + '/jobs/1/_stop'
    mock_method = mocker.patch.object(JobService, 'stop_by_id')
    response = client.get(api)
    assert_status_code(response)
    assert mock_method.called


def test_pause(client, api_url, mocker):
    """test pause """
    api = api_url + '/jobs/1/_pause'
    mock_method = mocker.patch.object(JobService, 'pause_by_id')
    response = client.get(api)
    assert_status_code(response)
    assert mock_method.called


def test_unpause(client, api_url, mocker):
    """test unpause"""
    api = api_url + '/jobs/1/_unpause'
    mock_method = mocker.patch.object(JobService, 'unpause_by_id')
    response = client.get(api)
    assert_status_code(response)
    assert mock_method.called
