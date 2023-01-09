"""test task detail"""
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_server.models import Task

from crawlerstack_spiderkeeper_server.utils.exceptions import ObjectDoesNotExist
from crawlerstack_spiderkeeper_server.repository.task_detail import TaskDetailRepository


@pytest.fixture()
async def repo():
    """repo fixture"""
    return TaskDetailRepository()


@pytest.mark.parametrize(
    'task_name, exist',
    [
        ('test1', True),
        ('test3', False)
    ]
)
async def test_get_task_detail_from_task_name(init_task_detail, repo, session, task_name, exist):
    """Test get a object."""
    if exist:
        exist_obj = await session.scalar(
            select(Task).filter(Task.name == task_name).options(selectinload(Task.task_details)))
        obj = await repo.get_task_detail_from_task_name(exist_obj.name)
        assert obj
        assert exist_obj.task_details[0].id == obj.id
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.get_task_detail_from_task_name(task_name)
