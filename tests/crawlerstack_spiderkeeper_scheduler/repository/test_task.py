"""test executor"""
import pytest
from sqlalchemy import select

from crawlerstack_spiderkeeper_scheduler.models import Task
from crawlerstack_spiderkeeper_scheduler.repository.task import TaskRepository
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    ObjectDoesNotExist


@pytest.fixture()
async def repo():
    """repo fixture"""
    return TaskRepository()


@pytest.mark.parametrize(
    'name, exist',
    [
        ('1_scheduler_', True),
        ('5_scheduler_', False)
    ]
)
async def test_get_by_name(init_task, repo, session, name, exist):
    """Test get a object."""
    if exist:
        exist_obj = await session.scalar(
            select(Task).where(Task.name == name))
        obj = await repo.get_by_name(exist_obj.name)
        assert obj
        assert exist_obj.id == obj.id
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.get_by_name(name)
