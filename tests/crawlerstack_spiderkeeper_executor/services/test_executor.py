"""test executor"""

import pytest

from crawlerstack_spiderkeeper_executor.executor import DockerExecutor
from crawlerstack_spiderkeeper_executor.schemas.base import (ExecutorSchema,
                                                             SpiderSchema,
                                                             TaskSchema)
from crawlerstack_spiderkeeper_executor.services import ExecutorService


@pytest.fixture
def executor_service():
    """executor service fixture"""
    return ExecutorService()


@pytest.fixture
def task_params():
    """task params fixture"""
    return TaskSchema(spider_params=SpiderSchema(
        DATA_URL='http://localhost:8080/data_url',
        LOG_URL='http://localhost:8080/log',
        METRICS='metrics',
        STORAGE_ENABLE=True,
        TASK_NAME='task_name'
    ),
        executor_params=ExecutorSchema(
            image='image',
            cmdline='cmdline',
            volume=None,
            environment=None
        ))


@pytest.mark.parametrize(
    'expect_value',
    [
        ('test_1',),
    ]
)
async def test_run(executor_service, task_params, mocker, expect_value):
    """test run"""
    run = mocker.patch.object(DockerExecutor, 'run', return_value=expect_value)
    result = await executor_service.run(task_params)
    assert result == expect_value
    run.assert_called_once()


@pytest.mark.parametrize(
    'container_id, expect_value',
    [
        ('test_1', 'running'),
        ('test_1', 'paused'),
    ]
)
async def test_check_by_id(executor_service, mocker, container_id, expect_value):
    """test check by id"""
    status = mocker.patch.object(DockerExecutor, 'status', return_value=expect_value)
    result = await executor_service.check_by_id(container_id)
    assert result == expect_value
    status.assert_called_once()


@pytest.mark.parametrize(
    'container_id',
    [
        ('test_1',),
    ]
)
async def test_check_by_id(executor_service, mocker, container_id):
    """test check by id"""
    delete = mocker.patch.object(DockerExecutor, 'delete')
    await executor_service.rm_by_id(container_id)
    delete.assert_called_once()
