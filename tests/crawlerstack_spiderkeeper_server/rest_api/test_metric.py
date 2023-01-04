"""test metric"""
from crawlerstack_spiderkeeper_server.services import MetricService
from tests.crawlerstack_spiderkeeper_server.rest_api.conftest import assert_status_code


def test_get(client, api_url, mocker):
    """test get"""
    api = api_url + '/metrics'
    get_method = mocker.patch.object(MetricService, 'get', return_value={'downloader_request_count': 2})
    response = client.get(api, params={'task_name': 'test'})
    assert_status_code(response)
    assert get_method.called
