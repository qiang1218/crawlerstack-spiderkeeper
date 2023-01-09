"""test job"""
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_server.models import Task

from crawlerstack_spiderkeeper_server.utils.exceptions import ObjectDoesNotExist
from crawlerstack_spiderkeeper_server.repository.job import JobRepository


@pytest.fixture()
async def repo():
    """repo fixture"""
    return JobRepository()


@pytest.mark.parametrize(
    'task_id, exist',
    [
        (1, True),
        (3, False)
    ]
)
async def test_get_job_from_task_id(init_task, repo, session, task_id, exist):
    """Test get a object."""
    if exist:
        exist_obj = await session.scalar(
            select(Task).filter(Task.id == task_id).options(selectinload(Task.job)))
        obj = await repo.get_job_from_task_id(exist_obj.id)
        assert obj
        assert exist_obj.job.id == obj.id
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.get_job_from_task_id(task_id)


@pytest.mark.parametrize(
    'task_name, exist',
    [
        ('test1', True),
        ('test3', False)
    ]
)
async def test_get_job_from_task_name(init_task, repo, session, task_name, exist):
    """Test get a object."""
    if exist:
        exist_obj = await session.scalar(
            select(Task).filter(Task.name == task_name).options(selectinload(Task.job)))
        obj = await repo.get_job_from_task_name(exist_obj.name)
        assert obj
        assert exist_obj.job.id == obj.id
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.get_job_from_task_name(task_name)
