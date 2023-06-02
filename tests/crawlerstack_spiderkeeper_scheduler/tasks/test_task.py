"""Test task"""
import pytest

from crawlerstack_spiderkeeper_scheduler.schemas.base import (ExecutorSchema,
                                                              SpiderSchema)
from crawlerstack_spiderkeeper_scheduler.services import ExecutorService
from crawlerstack_spiderkeeper_scheduler.tasks.task import Task as TaskRun
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    RemoteTaskRunError
from crawlerstack_spiderkeeper_scheduler.utils.request import \
    RequestWithSession
from crawlerstack_spiderkeeper_scheduler.utils.status import Status


class TestTask:
    """Test task"""

    @pytest.fixture
    def task(self, settings):
        """Task fixture"""
        return TaskRun(settings)

    @pytest.fixture
    def executor_server(self):
        """Executor server fixture"""
        return ExecutorService()

    @pytest.mark.parametrize(
        'executor_type, status, except_value',
        [
            ('docker', Status.ONLINE.value, 2),
        ]
    )
    async def test_get_active_executors(self, init_executor, task, executor_server, session, executor_type, status,
                                        except_value, mocker):
        """Test get active executors"""
        executors = await executor_server.get()
        mocker.patch.object(RequestWithSession, 'request', return_value={'data': executors})
        result = task.get_active_executors(executor_type, status)  # noqa
        assert len(result) == except_value

    def test_run_task(self, task, mocker):
        """Test run task"""
        request = mocker.patch.object(RequestWithSession, 'request',
                                      return_value={'message': 'ok', 'data': {'container_id': 'task_1'}})
        task.run_task(url='http://localhost:8082/api/vi/_run', params={'job_id': 'task_1'})
        request.assert_called_once()

    def test_run_task_failed(self, task, mocker):
        """Test run task failed"""
        request = mocker.patch.object(RequestWithSession, 'request', return_value={'message': 'ok'})
        with pytest.raises(RemoteTaskRunError):
            task.run_task(url='http://localhost:2375', params={'job_id': 'task_1 '})
        request.assert_called_once()

    def test_create_server_task_record(self, task, mocker):
        """Test create server task record"""
        request = mocker.patch.object(RequestWithSession, 'request', return_value={'data': {'id': 1}})
        task_id = task.create_server_task_record(task_name='1-scheduled-20230109175203', job_id='1')
        assert task_id == 1
        request.assert_called_once()

    async def test_choose_executor(self, init_executor, executor_server, session, task, mocker):
        """Test choose executor"""
        executors = await executor_server.get()
        get_active_executors = mocker.patch.object(TaskRun, 'get_active_executors', return_value=executors)
        executor = task.choose_executor('docker', '')
        assert executor
        get_active_executors.assert_called_once()

    async def test_run(self, init_executor, executor_server, task, session, mocker):
        """Test run"""

        spider_params = SpiderSchema(
            DATA_URL='data_url',
            LOG_URL='log_url',
            METRICS_URL='metrics',
            STORAGE_ENABLE=False,
            SNAPSHOT_ENABLE=False,
            TASK_NAME='test_task_name'
        )
        executor_params = ExecutorSchema(
            image='python:3.10',
            cmdline="['python','-c', 'for i in range(100):import logging;logging.error(i);"
                    "import time;time.sleep(0.1)']",
            volume=None,
            environment=None,
            executor_type='docker',
            executor_selector='',
        )
        kwargs = {
            'spider_params': spider_params.dict(),
            'executor_params': executor_params.dict(),
            'job_id': '1',
        }
        executors = await executor_server.get()
        get_active_executor = mocker.patch.object(TaskRun, 'get_active_executors', return_value=executors)
        run_task = mocker.patch.object(TaskRun, 'run_task', return_value='container_id')
        create_scheduler_task_record = mocker.patch.object(TaskRun, 'create_scheduler_task_record')
        create_server_task_record = mocker.patch.object(TaskRun, 'create_server_task_record')

        task.run(**kwargs)

        get_active_executor.assert_called_once()
        run_task.assert_called_once()
        create_scheduler_task_record.assert_called_once()
        create_server_task_record.assert_called_once()
