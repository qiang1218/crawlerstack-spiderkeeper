"""test task"""
from datetime import datetime

import pytest
from sqlalchemy import select

from crawlerstack_spiderkeeper_scheduler.models import Task
from crawlerstack_spiderkeeper_scheduler.schemas.task import (TaskCreate,
                                                              TaskSchema,
                                                              TaskUpdate)
from crawlerstack_spiderkeeper_scheduler.services.task import TaskService
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    ObjectDoesNotExist


@pytest.fixture()
def service():
    """service fixture"""
    return TaskService()


@pytest.mark.parametrize(
    'executor_id, exist',
    [
        (1, True),
        (100, False)
    ]
)
async def test_create(init_executor, session, service, executor_id, exist):
    """test create"""
    obj_in = TaskCreate(name="1_scheduler_",
                        url="http://localhost:2375",
                        type="docker",
                        executor_id=executor_id,
                        status=1,
                        container_id='d343j4er',
                        job_id=1)
    if exist:
        await service.create(obj_in=obj_in)
        count = await service.count()
        assert count == 1
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.create(obj_in=obj_in)


@pytest.mark.parametrize(
    'pk, executor_id, exist',
    [
        (1, 1, True),
        (1, 5, False),
        (100, 1, False)
    ]
)
async def test_update_by_id(init_task, session, service, pk, executor_id, exist):
    """test update by id"""
    obj_in = TaskUpdate(status=3, executor_id=executor_id, task_end_time=datetime.now())
    if exist:
        before = await service.get_by_id(pk)
        await service.update_by_id(pk, obj_in=obj_in)
        after = await service.get_by_id(pk)
        assert before
        assert after.status != before.status
        assert after.status == obj_in.status
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.update_by_id(pk, obj_in=obj_in)


@pytest.mark.parametrize(
    'name, status, exist',
    [
        ('1_scheduler_', 3, True),
        ('100_scheduler_', 3, False)
    ]
)
async def test_update_by_name(init_task, session, service, name, status, exist):
    """Test update by name"""
    obj_in = TaskUpdate(status=status, task_end_time=datetime.now())
    if exist:
        stmt = select(Task).where(Task.name == name)
        obj = await session.scalar(stmt)
        before = TaskSchema.from_orm(obj)
        after = await service.update_by_name(name, obj_in=obj_in)
        assert after.status != before.status
        assert after.status == status
    else:
        after = await service.update_by_name(name, obj_in=obj_in)
        assert not after
