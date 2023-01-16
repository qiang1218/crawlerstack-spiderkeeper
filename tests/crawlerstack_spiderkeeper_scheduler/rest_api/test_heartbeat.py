"""task heartbeat"""

from crawlerstack_spiderkeeper_scheduler.utils.status import Status
from tests.crawlerstack_spiderkeeper_scheduler.rest_api.conftest import \
    assert_status_code


def test_heartbeat(client, init_executor, api_url):
    """test heartbeat"""
    api = api_url + '/heartbeats/1'
    data = {'memory': 16, 'cpu': 70, 'status': Status.ONLINE.value}
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('message') == 'ok'

    api = api_url + '/executors/1'
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('data').get('cpu') == data.get('cpu')
