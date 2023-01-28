"""Test task"""
from crawlerstack_spiderkeeper_forwarder.services import DataService
from tests.crawlerstack_spiderkeeper_forwarder.rest_api.conftest import \
    assert_status_code


def test_create(client, api_url, mocker):
    """test create"""
    api = api_url + '/datas'
    data = {
        'task_name': 'test',
        'data': {
            'title': 'user',
            'fields': ['name', 'age', 'gender'],
            'datas': [('zhangSan', 10, 0), ('liHua', 25, 1)]
        }
    }
    create = mocker.patch.object(DataService, 'create', return_value={})
    response = client.post(api, json=data)

    assert_status_code(response)
    assert response.json().get('message') == 'ok'
    create.assert_called_once()
