"""test executor"""
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_scheduler.models import Executor
from crawlerstack_spiderkeeper_scheduler.repository.executor import \
    ExecutorRepository
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    ObjectDoesNotExist
from crawlerstack_spiderkeeper_scheduler.utils.status import Status


@pytest.fixture()
async def repo():
    """repo fixture"""
    return ExecutorRepository()


@pytest.mark.parametrize(
    'name, exist',
    [
        ('docker_executor_1', True),
        ('docker_executor_3', False)
    ]
)
async def test_get_by_name(init_executor, repo, session, name, exist):
    """Test get a object."""
    if exist:
        exist_obj = await session.scalar(
            select(Executor).where(Executor.name == name))
        obj = await repo.get_by_name(exist_obj.name)
        assert obj
        assert exist_obj.id == obj.id
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.get_by_name(name)
