"""test task"""
from datetime import datetime

import pytest

from crawlerstack_spiderkeeper_scheduler.services import TaskService
from crawlerstack_spiderkeeper_scheduler.tasks.task_life_cycle import LifeCycle
from crawlerstack_spiderkeeper_scheduler.utils.request import RequestWithHttpx


class TestLifeCycle:
    """test task"""

    @pytest.fixture
    def life_cycle_task(self):
        """Life cycle task fixture"""
        return LifeCycle()

    async def test_get_executors(self, life_cycle_task, init_executor):
        """Test get executors"""
        result = await life_cycle_task.get_executors()
        assert len(result) == 2

    async def test_get_all_containers(self, life_cycle_task, mocker):
        """Test get all containers"""
        data = {'data': [{'container_id': 'foo', 'status': 5, 'task_name': 'foo'}]}
        request = mocker.patch.object(RequestWithHttpx, 'request', return_value=data)
        result = await life_cycle_task.get_all_containers('http://localhost')
        assert result
        request.assert_called_once()

    async def test_update_task_record(self, life_cycle_task, mocker):
        """Test update task record"""
        task_name = 'foo'
        status = 5
        task_end_time = datetime.now()
        update_by_name = mocker.patch.object(TaskService, 'update_by_name')
        await life_cycle_task.update_task_record(task_name, status, task_end_time)
        update_by_name.assert_called_once()

    async def test_update_server_task_record(self, life_cycle_task, mocker):
        """Test update server task record"""
        request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'data': [{'id': 1}]})
        await life_cycle_task.update_server_task_record(task_name='foo', task_status=5)
        request.assert_called()
