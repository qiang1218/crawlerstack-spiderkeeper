"""test executor"""
import inspect

import pytest

from crawlerstack_spiderkeeper_scheduler.schemas.executor import (
    ExecutorCreate, ExecutorUpdate)
from crawlerstack_spiderkeeper_scheduler.services.executor import \
    ExecutorService
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    ObjectDoesNotExist
from crawlerstack_spiderkeeper_scheduler.utils.status import Status


@pytest.fixture()
def service():
    """service fixture"""
    return ExecutorService()


async def test_create(init_executor, session, service):
    """test create"""
    obj_in = ExecutorCreate(name="docker_executor_3", selector="test", url="http://localhost:2375", type="docker",
                            memory=32, cpu=50)
    await service.create(obj_in=obj_in)
    count = await service.count()
    assert count == 3


async def test_create_exist(init_executor, session, service):
    """test create"""
    obj_in = ExecutorCreate(name="docker_executor_1", selector="test", url="http://localhost:2375", type="docker",
                            memory=32, cpu=50)
    await service.create(obj_in=obj_in)
    count = await service.count()
    assert count == 2


@pytest.mark.parametrize(
    'pk, expect_value',
    [
        (1, 'changed_value'),
        (100, ObjectDoesNotExist)
    ]
)
async def test_heartbeat(init_executor, session, service, pk, expect_value):
    """test heartbeat"""
    changed = Status.OFFLINE.value
    if inspect.isclass(expect_value):
        with pytest.raises(expect_value):
            await service.update(pk, ExecutorUpdate(status=changed))  # noqa
    else:
        obj = await service.update(pk, ExecutorUpdate(status=changed))  # noqa
        assert obj.status == changed
