"""test task"""
import datetime

import pytest

from crawlerstack_spiderkeeper_scheduler.services import ExecutorService
from crawlerstack_spiderkeeper_scheduler.tasks.task import Task as TaskRun
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    RemoteTaskRunError
from crawlerstack_spiderkeeper_scheduler.utils.request import \
    RequestWithSession
from crawlerstack_spiderkeeper_scheduler.utils.status import Status


class TestTask:
    """test task"""

    @pytest.fixture
    def task(self, settings):
        """task fixture"""
        return TaskRun(settings)

    @pytest.fixture
    def executor_server(self):
        """executor server fixture"""
        return ExecutorService()

    # @pytest.mark.parametrize(
    #     'executor_type, status, except_value',
    #     [
    #         ('docker', Status.ONLINE.value, 2),
    #     ]
    # )
    # async def test_get_active_executors(self, init_executor, task, session, executor_type, status,
    #                                     except_value):
    #     """test get active executors"""
    #     result = await task.get_active_executors(executor_type, status)  # noqa
    #     assert len(result) == except_value

    def test_run_task(self, task, mocker):
        """test run task"""
        request = mocker.patch.object(RequestWithSession, 'request',
                                      return_value={'message': 'ok', 'data': {'container_id': 'task_1'}})
        task.run_task(url='http://localhost:8082/api/vi/_run', params={'job_id': 'task_1'})
        request.assert_called_once()

    def test_run_task_failed(self, task, mocker):
        """test run task failed"""
        request = mocker.patch.object(RequestWithSession, 'request', return_value={'message': 'ok'})
        with pytest.raises(RemoteTaskRunError):
            task.run_task(url='http://localhost:2375', params={'job_id': 'task_1 '})
        request.assert_called_once()

    def test_get_task_status(self, task, mocker):
        """test get task status"""
        request = mocker.patch.object(RequestWithSession, 'request',
                                      return_value={'message': 'ok', 'data': {'container_id': 'task_1', 'status': 1}})
        result = task.get_task_status(url='http://localhost:2375', container_id='task_1')
        assert result == 1
        request.assert_called_once()

    # async def test_update_task_record(self, init_task, task, session):
    #     """test update task record"""
    #     kwargs = {
    #         'status': Status.FINISH.value,
    #         'task_end_time': datetime.datetime.now()
    #     }
    #     result = await task.update_task_record(pk=1, **kwargs)
    #     assert result.status == kwargs.get('status')
    #     assert result.task_end_time == kwargs.get('task_end_time')

    def test_create_server_task_record(self, task, mocker):
        """test create server task record"""
        request = mocker.patch.object(RequestWithSession, 'request', return_value={'data': {'id': 1}})
        task.create_server_task_record(task_name='1-scheduled-20230109175203')
        request.assert_called_once()

    def test_update_server_task_record(self, task, mocker):
        """test update server task record"""
        request = mocker.patch.object(RequestWithSession, 'request', return_value={'data': {'id': 1}})
        task.update_server_task_record(pk=1, status=Status.FINISH.value)  # noqa
        request.assert_called_once()

    # @pytest.mark.parametrize(
    #     'symbol, except_value',
    #     [
    #         (True, 2),
    #         (False, 0)
    #     ]
    # )
    # async def test_update_task_count(self, init_executor, task, session, symbol, except_value):
    #     """test update task count"""
    #     before = await task.executor_server.get_by_id(pk=1)
    #     assert before.task_count == 1
    #     # 修改
    #     await task.update_task_count(before, symbol)
    #     # 在查询
    #     after = await task.executor_server.get_by_id(pk=1)
    #     assert after.task_count == except_value

    async def test_run(self, init_executor, task, session, mocker):
        """test run"""
        # kwargs = {
        #     'spider_params': {},
        #     'executor_params': {},
        #     'job_id': ''
        # }

        # spider_params = SpiderSchema(
        #     DATA_URL='data_url',
        #     LOG_URL='log_url',
        #     METRICS='metrics',
        #     STORAGE_ENABLE=False,
        #     TASK_NAME='test_task_name'
        # ),
        # executor_params = ExecutorSchema(
        #     image='python:3.10',
        #     cmdline="['python','-c', 'for i in range(100):import logging;logging.error(i);"
        #     "import time;time.sleep(0.1)']",
        #     volume=None,
        #     environment=None
        # ))
        # todo 继续完善
