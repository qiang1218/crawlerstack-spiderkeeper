"""test executor"""
from crawlerstack_spiderkeeper_executor.services.executor import \
    ExecutorService
from tests.crawlerstack_spiderkeeper_executor.rest_api.conftest import \
    assert_status_code


async def test_run(client, api_url, mocker):
    """test run"""
    api = api_url + '/_run'
    data = {'spider_params': {'DATA_URL': '',
                              'LOG_URL': '',
                              'METRICS_URL': '',
                              'STORAGE_ENABLE': True,
                              'SNAPSHOT_ENABLE': True,
                              'TASK_NAME': 'test'},
            'executor_params': {'image': '',
                                'cmdline': '',
                                'volume': None,
                                'environment': None}}
    run = mocker.patch.object(ExecutorService, 'run', return_value='container_id')
    response = client.post(api, json=data)
    assert_status_code(response)
    run.assert_called_once()


async def test_check(client, api_url, mocker):
    """test check"""
    api = api_url + '/_check/1'
    check_by_id = mocker.patch.object(ExecutorService, 'check_by_id', return_value='running')
    response = client.get(api)
    assert_status_code(response)
    check_by_id.assert_called_once()


async def test_rm(client, api_url, mocker):
    """test rm"""
    api = api_url + '/_rm/1'
    run = mocker.patch.object(ExecutorService, 'rm_by_id', return_value='')
    response = client.get(api)
    assert_status_code(response)
    run.assert_called_once()


async def test_get(client, api_url, mocker):
    """test rm"""
    api = api_url + '/containers'
    get = mocker.patch.object(ExecutorService, 'get',
                              return_value=[{'container_id': 'test', 'status': 'exited', 'task_name': 'test'}])
    response = client.get(api)
    assert_status_code(response)
    get.assert_called_once()
