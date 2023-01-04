"""rest api"""
import pytest
from fastapi_sa.database import db
from crawlerstack_spiderkeeper_scheduler.models import Executor, ExecutorDetail, Task
from fastapi import Response


@pytest.fixture()
async def init_executor():
    """Init executor fixture."""
    async with db():
        executors = [
            Executor(name="docker_executor_1", selector="test", url="http://localhost:2375", type="docker", memory="32",
                     cpu="50"),
            Executor(name="docker_executor_2", selector="test", url="http://localhost:2376", type="docker", memory="32",
                     cpu="50"),
        ]
        db.session.add_all(executors)
        await db.session.flush()


@pytest.fixture()
async def init_executor_detail(init_executor):
    """Init executor detail fixture."""
    async with db():
        executor_details = [
            ExecutorDetail(task_count=1, executor_id=1),
            ExecutorDetail(task_count=2, executor_id=2),
        ]
        db.session.add_all(executor_details)
        await db.session.flush()


@pytest.fixture()
async def init_task(init_executor):
    """Init task fixture."""
    async with db():
        tasks = [
            Task(name="1_scheduler_", url="http://localhost:2375", type="docker", executor_id=1, status=1,
                 container_id='d343j4er'),
            Task(name="2_scheduler_", url="http://localhost:2375", type="docker", executor_id=1, status=1,
                 container_id='d343j4er'),
        ]
        db.session.add_all(tasks)
        await db.session.flush()


def assert_status_code(response: Response, code=200) -> None:
    """Check state code is ok."""
    assert response.status_code == code
