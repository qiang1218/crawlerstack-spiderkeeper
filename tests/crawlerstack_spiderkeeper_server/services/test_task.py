"""test task"""
import pytest

from crawlerstack_spiderkeeper_server.services.task import TaskService
from crawlerstack_spiderkeeper_server.schemas.task import TaskCreate, TaskUpdate
from crawlerstack_spiderkeeper_server.utils.exceptions import ObjectDoesNotExist


@pytest.fixture()
def service():
    """service fixture"""
    return TaskService()


@pytest.mark.parametrize(
    'job_id, exist',
    [
        (1, True),
        (100, False)
    ]
)
async def test_create(init_job, session, service, job_id, exist):
    """test create"""
    obj_in = TaskCreate(name="test1", job_id=job_id)
    if exist:
        await service.create(obj_in=obj_in)
        count = await service.count()
        assert count == 1
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.create(obj_in=obj_in)


@pytest.mark.parametrize(
    'pk, job_id, exist',
    [
        (1, 1, True),
        (1, None, True),
        (1, 5, False),
        (100, 1, False)
    ]
)
async def test_update_by_id(init_task, session, service, pk, job_id, exist):
    """test update by id"""
    obj_in = TaskUpdate(status=3, job_id=job_id)
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
    'pk, job_name, exist',
    [
        (1, 'test1', True),
        (100, None, False)
    ]
)
async def test_job_from_task_id(init_task, session, service, pk, job_name, exist):
    """test get project from artifact"""
    if exist:
        result = await service.get_job_from_task_id(pk)
        assert result
        assert result.name == job_name
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.get_job_from_task_id(pk)
