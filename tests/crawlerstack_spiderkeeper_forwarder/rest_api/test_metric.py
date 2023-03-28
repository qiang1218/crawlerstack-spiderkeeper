"""Test metric"""
from crawlerstack_spiderkeeper_forwarder.services import MetricService
from tests.crawlerstack_spiderkeeper_forwarder.rest_api.conftest import \
    assert_status_code


def test_create(client, api_url, mocker):
    """test create"""
    api = api_url + '/metrics'
    data = {
        'task_name': 'test',
        'data': {
            'downloader_request_count': 5,
            'downloader_request_bytes': 342,
            'downloader_request_method_count_GET': 0,
            'downloader_response_count': 0,
            'downloader_response_status_count_200': 5,
            'downloader_response_status_count_302': 0,
            'downloader_response_bytes': 1024,
            'downloader_exception_count': 0
        }
    }
    create = mocker.patch.object(MetricService, 'create', return_value={})
    response = client.post(api, json=data)

    assert_status_code(response)
    assert response.json().get('message') == 'ok'
    create.assert_called_once()
