"""test base service"""
import inspect

import pytest
from sqlalchemy import func, select

from crawlerstack_spiderkeeper_scheduler.models import Executor
from crawlerstack_spiderkeeper_scheduler.schemas.executor import (
    ExecutorCreate, ExecutorSchema, ExecutorUpdate)
from crawlerstack_spiderkeeper_scheduler.services.executor import \
    ExecutorService
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    ObjectDoesNotExist


class TestEntityService:
    """Test entity service"""

    @pytest.fixture()
    def service(self):
        """service fixture"""
        return ExecutorService()

    async def test_get_by_id(self, init_executor, session, service):
        """test get by id"""
        exist_obj = await session.scalar(select(Executor))
        obj = await service.get_by_id(exist_obj.id)
        assert obj.id == exist_obj.id

    async def test_get(self, init_executor, session, service):
        """test get"""
        objs = await service.get()
        stmt = select(func.count()).select_from(Executor)
        assert len(objs) == await session.scalar(stmt)

    async def test_create(self, session, service):
        """test create"""
        obj_in = ExecutorCreate(name="test1", selector='test', url="http://localhost:2375", type='docker', memory=32,
                                cpu=80)
        obj = await service.create(obj_in=obj_in)
        assert obj
        assert isinstance(obj, ExecutorSchema)

        stmt = select(func.count()).select_from(Executor)
        assert await session.scalar(stmt) == 1

    @pytest.mark.parametrize(
        'pk, expect_value',
        [
            (1, 'changed_value'),
            (100, ObjectDoesNotExist)
        ]
    )
    async def test_update(self, init_executor, session, service, pk, expect_value):
        """test update"""
        changed = 'http://localhost:2376'
        if inspect.isclass(expect_value):
            with pytest.raises(expect_value):
                await service.update(pk, ExecutorUpdate(url=changed))
        else:
            obj = await service.update(pk, ExecutorUpdate(url=changed))
            assert obj.url == changed

    @pytest.mark.parametrize(
        'pk, exist',
        [
            (1, True),
            (100, False)
        ]
    )
    async def test_delete(self, init_executor, session, service, pk, exist):
        """test delete"""
        if exist:
            stmt = select(func.count()).select_from(Executor)
            before_count = await session.scalar(stmt)
            obj = await session.scalar(select(Executor))
            await service.delete_by_id(pk=obj.id)
            after_count = await session.scalar(stmt)
            assert before_count - 1 == after_count
        else:
            with pytest.raises(ObjectDoesNotExist):
                await service.delete_by_id(pk=pk)

    async def test_count(self, init_executor, session, service):
        """test count"""
        count = await service.count()
        assert count == 2
