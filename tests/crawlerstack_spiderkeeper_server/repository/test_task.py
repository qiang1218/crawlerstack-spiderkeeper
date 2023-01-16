"""test task"""
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_server.models import TaskDetail
from crawlerstack_spiderkeeper_server.repository.task import TaskRepository
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist


@pytest.fixture()
async def repo():
    """repo fixture"""
    return TaskRepository()


@pytest.mark.parametrize(
    'task_detail_id, exist',
    [
        (1, True),
        (3, False)
    ]
)
async def test_get_task_from_task_detail_id(init_task_detail, repo, session, task_detail_id, exist):
    """Test get a object."""
    if exist:
        exist_obj = await session.scalar(
            select(TaskDetail).filter(TaskDetail.id == task_detail_id).options(selectinload(TaskDetail.task)))
        obj = await repo.get_task_from_task_detail_id(exist_obj.id)
        assert obj
        assert exist_obj.task.id == obj.id
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.get_task_from_task_detail_id(task_detail_id)
