"""test task"""
from datetime import datetime

import pytest

from crawlerstack_spiderkeeper_scheduler.schemas.task import (TaskCreate,
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
    obj_in = TaskCreate(name="1_scheduler_", url="http://localhost:2375", type="docker", executor_id=executor_id, status=1,
                        container_id='d343j4er')
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
