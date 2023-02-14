"""test task detail"""
import pytest

from crawlerstack_spiderkeeper_server.schemas.task_detail import (
    TaskDetailCreate, TaskDetailUpdate)
from crawlerstack_spiderkeeper_server.services.task_detail import \
    TaskDetailService
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist


@pytest.fixture()
def service():
    """service fixture"""
    return TaskDetailService()


@pytest.mark.parametrize(
    'task_id, exist',
    [
        (1, True),
        (100, False)
    ]
)
async def test_create(init_task, session, service, task_id, exist):
    """test create"""
    obj_in = TaskDetailCreate(item_count=2, task_id=task_id)
    if exist:
        await service.create(obj_in=obj_in)
        count = await service.count()
        assert count == 1
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.create(obj_in=obj_in)


@pytest.mark.parametrize(
    'pk, task_id, exist',
    [
        (1, 1, True),
        (1, 5, False),
        (100, 1, False)
    ]
)
async def test_update_by_id(init_task_detail, session, service, pk, task_id, exist):
    """test update by id"""
    obj_in = TaskDetailUpdate(item_count=5, task_id=task_id)
    if exist:
        before = await service.get_by_id(pk)
        await service.update_by_id(pk, obj_in=obj_in)
        after = await service.get_by_id(pk)
        assert before
        assert after.item_count != before.item_count
        assert after.item_count == obj_in.item_count
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.update_by_id(pk, obj_in=obj_in)


@pytest.mark.parametrize(
    'pk, task_name, exist',
    [
        (1, 'test1', True),
        (100, None, False)
    ]
)
async def test_get_task_from_task_detail_id(init_task_detail, session, service, pk, task_name, exist):
    """test get task from task detail id"""
    if exist:
        result = await service.get_task_from_task_detail_id(pk)
        assert result
        assert result.name == task_name
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.get_task_from_task_detail_id(pk)
