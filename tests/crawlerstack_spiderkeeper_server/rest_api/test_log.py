"""test log"""
from crawlerstack_spiderkeeper_server.services import LogService
from tests.crawlerstack_spiderkeeper_server.rest_api.conftest import assert_status_code


def test_get(client, api_url, mocker):
    """test get"""
    api = api_url + '/logs'
    get_method = mocker.patch.object(LogService, 'get', return_value=['line1', 'line2'])
    response = client.get(api, params={'task_name': 'test', 'line': 2})
    assert_status_code(response)
    assert len(response.json().get('data')) == 2
    assert get_method.called
