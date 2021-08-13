"""
Test base service.
"""
import asyncio
import functools
import inspect
import json
from asyncio import AbstractEventLoop
from concurrent.futures import Future
from datetime import datetime
from typing import Dict, Any

import pytest
from kombu import Message, Queue, Exchange, Consumer
from sqlalchemy import func, select, text

from crawlerstack_spiderkeeper.db.models import Audit
from crawlerstack_spiderkeeper.schemas.audit import AuditCreate, AuditUpdate
from crawlerstack_spiderkeeper.services import AuditService
from crawlerstack_spiderkeeper.services.utils import Kombu
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist


class TestBaseService:
    """Test base service."""

    @pytest.mark.asyncio
    async def test_get_return_no_result(self, migrate, factory_with_session):
        """Test no object when get multi."""
        async with factory_with_session(AuditService) as service:
            objs = await service.get()
        assert objs == []

    @pytest.mark.asyncio
    async def test_get(self, init_audit, session, factory_with_session):
        """Test get multi object."""
        async with factory_with_session(AuditService) as service:
            objs = await service.get()
        stmt = select(func.count()).select_from(Audit)
        assert len(objs) == await session.scalar(stmt)

    @pytest.mark.asyncio
    async def test_get_by_id(self, init_audit, session, factory_with_session):
        """Test get a object."""
        exist_obj = await session.scalar(select(Audit))

        async with factory_with_session(AuditService) as service:
            obj = await service.get_by_id(exist_obj.id)

        assert obj.id == exist_obj.id

    @pytest.mark.asyncio
    async def test_get_by_id_with_no_data(self, migrate, factory_with_session):
        """Test get a not exist object."""
        async with factory_with_session(AuditService) as service:
            with pytest.raises(ObjectDoesNotExist):
                await service.get_by_id(1)

    @pytest.mark.asyncio
    async def test_create(self, migrate, session, factory_with_session):
        """Test create a object."""
        async with factory_with_session(AuditService) as service:
            obj_in = AuditCreate(
                url='https://example.com',
                method='POST',
                detail='foo',
                client='127.0.0.1'
            )
            obj = await service.create(obj_in=obj_in)
            assert obj
            assert isinstance(obj, Audit)
            stmt = select(func.count()).select_from(Audit)

        assert await session.scalar(stmt) == 1

    @pytest.mark.parametrize(
        'pk, expect_value',
        [
            (1, 'changed_value'),
            (100, ObjectDoesNotExist)
        ]
    )
    @pytest.mark.asyncio
    async def test_update(self, init_audit, factory_with_session, pk, expect_value):
        """Test update a object."""
        changed = 'test_update'
        async with factory_with_session(AuditService) as service:
            if inspect.isclass(expect_value) and issubclass(expect_value, Exchange):
                with pytest.raises(expect_value):
                    await service.update_by_id(1, AuditUpdate(detail=changed))
            else:
                obj = await service.update_by_id(1, AuditUpdate(detail=changed))
                assert obj.detail == changed

    @pytest.mark.asyncio
    async def test_delete(self, init_audit, session, factory_with_session):
        """Test delete a object."""
        stmt = select(func.count()).select_from(Audit)

        async with session.begin():
            before_count = await session.scalar(stmt)
            obj = await session.scalar(select(Audit))

        async with factory_with_session(AuditService) as service:
            await service.delete_by_id(pk=obj.id)

        async with session.begin():
            after_count = await session.scalar(stmt)

        assert before_count - 1 == after_count

    @pytest.mark.asyncio
    async def test_delete_no_exist(self, migrate, factory_with_session):
        """Test delete a not exist object."""
        async with factory_with_session(AuditService) as service:
            with pytest.raises(ObjectDoesNotExist):
                await service.delete_by_id(pk=1)

    @pytest.mark.asyncio
    async def test_count(self, init_audit, factory_with_session):
        async with factory_with_session(AuditService) as service:
            result = await service.count()
            assert result == 2


# ===================

class DemoKombu(Kombu):
    """Demo Kombu mixin."""
    NAME = 'test'


@pytest.mark.asyncio
async def test_kombu():
    """
    test kombu
    :return:
    """
    kombu = DemoKombu()

    await kombu.publish(
        queue_name='foo',
        routing_key='bar',
        body=json.dumps({
            'datetime': datetime.now().strftime('%Y-%h-%mT%H:%M:%S+0800'),
            'msg': 'foo'
        })
    )

    await asyncio.sleep(0.2)

    async def use_data(data):
        """consume then have to do some coroutine"""
        await asyncio.sleep(0.1)
        data = json.loads(data)
        assert data['msg'] == 'foo'

    def consume_and_auto_ack(loop: AbstractEventLoop, body, message):
        """Registered the callback to consumer """
        # To submit a coroutine object to the event loop. (thread safe)
        fut = asyncio.run_coroutine_threadsafe(use_data(body), loop)
        fut.result()  # Wait for the result from other os thread
        message.ack()  # then manual ack

    callback = functools.partial(consume_and_auto_ack, asyncio.get_running_loop())
    await kombu.consume(
        queue_name='foo',
        routing_key='bar',
        limit=1,
        register_callbacks=[callback],
    )
