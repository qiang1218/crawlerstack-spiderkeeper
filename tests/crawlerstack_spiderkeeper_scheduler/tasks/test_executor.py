"""Test executor"""
import asyncio

import pytest

from crawlerstack_spiderkeeper_scheduler.tasks import ExecutorTask
from crawlerstack_spiderkeeper_scheduler.utils.status import Status


@pytest.fixture
def executor_task():
    """Executor task fixture"""
    return ExecutorTask()


async def test_start_and_stop(executor_task):
    """Test start and stop"""
    await executor_task.server_start()
    await asyncio.sleep(2)
    assert executor_task._server_running  # pylint: disable=W0212
    await executor_task.server_stop()
    assert not executor_task._server_running  # pylint: disable=W0212


async def test_run_wrapper(executor_task, session, init_executor):
    """Test run wrapper"""
    # 默认都为开启状态
    before = await executor_task.executor_service.get(search_fields={'status': Status.ONLINE.value})
    await executor_task._run_wrapper()  # pylint: disable=W0212
    after = await executor_task.executor_service.get(search_fields={'status': Status.OFFLINE.value})
    assert len(before) == len(after)
