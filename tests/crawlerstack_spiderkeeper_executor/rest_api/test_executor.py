"""test executor"""
from crawlerstack_spiderkeeper_executor.executor import DockerExecutor
from crawlerstack_spiderkeeper_executor.services.executor import \
    ExecutorService
from tests.crawlerstack_spiderkeeper_executor.rest_api.conftest import \
    assert_status_code


async def test_run(client, api_url, mocker):
    """test run"""
    api = api_url + '/_run'
    data = {'spider_params': {'DATA_URL': '',
                              'LOG_URL': '',
                              'METRICS': '',
                              'STORAGE_ENABLE': True,
                              'TASK_NAME': 'test'},
            'executor_params': {'image': '',
                                'cmdline': '',
                                'volume': None,
                                'environment': None}}
    mock_method = mocker.patch.object(ExecutorService, 'run')
    response = client.post(api, json=data)
    assert_status_code(response)
    assert mock_method.called


async def test_check(client, api_url, mocker):
    """test check"""
    api = api_url + '/_check/1'
    mock_method = mocker.patch.object(ExecutorService, 'check_by_id')
    response = client.get(api)
    assert_status_code(response)
    assert mock_method.called


async def test_rm(client, api_url, mocker):
    """test rm"""
    api = api_url + '/_rm/1'
    mock_method = mocker.patch.object(ExecutorService, 'run')
    response = client.get(api)
    # assert_status_code(response)
    assert mock_method.called
