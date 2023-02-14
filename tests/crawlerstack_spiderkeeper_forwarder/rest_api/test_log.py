"""Test log"""
from crawlerstack_spiderkeeper_forwarder.services import LogService
from tests.crawlerstack_spiderkeeper_forwarder.rest_api.conftest import \
    assert_status_code


def test_create(client, api_url, mocker):
    """test create"""
    api = api_url + '/logs'
    data = {
        'task_name': 'test',
        'data': ['line1', 'line2', 'line3']
    }
    create = mocker.patch.object(LogService, 'create', return_value={})
    response = client.post(api, json=data)

    assert_status_code(response)
    assert response.json().get('message') == 'ok'
    create.assert_called_once()
