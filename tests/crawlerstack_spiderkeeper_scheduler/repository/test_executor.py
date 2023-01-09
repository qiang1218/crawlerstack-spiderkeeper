"""test job"""
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_scheduler.models import Executor

from crawlerstack_spiderkeeper_scheduler.utils.exceptions import ObjectDoesNotExist
from crawlerstack_spiderkeeper_scheduler.repository.executor import ExecutorRepository

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


@pytest.mark.parametrize(
    'executor_type, status, exist',
    [
        ('docker', Status.ONLINE.value, True),
        ('docker1', Status.OFFLINE.value, False),
    ]
)
async def test_get_by_type_join_detail(init_executor_detail, repo, session, executor_type, status, exist):
    """Test get a object."""
    if exist:
        exist_obj = await session.scalars(
            select(Executor).filter(Executor.type == executor_type, Executor.status == status).options(
                selectinload(Executor.executor_detail)))
        obj = await repo.get_by_type_join_detail(executor_type, status)  # noqa
        assert obj
        assert len(exist_obj.all()) == len(obj)
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.get_by_type_join_detail(executor_type, status)  # noqa
