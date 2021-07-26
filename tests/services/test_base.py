"""
Test base service.
"""
from typing import Dict

import pytest
from kombu import Message
from sqlalchemy import select, func, text

from crawlerstack_spiderkeeper.db.models import Audit
from crawlerstack_spiderkeeper.schemas.audit import AuditCreate, AuditUpdate
from crawlerstack_spiderkeeper.services import AuditService
from crawlerstack_spiderkeeper.services.base import KombuMixin
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

    @pytest.mark.asyncio
    async def test_update(self, init_audit, session, factory_with_session):
        """Test update a object."""
        exist_obj = await session.scalar(select(Audit))
        changed = 'test_update'
        async with factory_with_session(AuditService) as service:
            obj = await service.update_by_id(exist_obj.id, AuditUpdate(detail=changed))
        assert exist_obj.detail != obj.detail

    @pytest.mark.asyncio
    async def test_update_obj_not_exist(self, migrate, factory_with_session):
        """Test update a not exist object."""
        async with factory_with_session(AuditService) as service:
            with pytest.raises(ObjectDoesNotExist):
                changed = 'test_update'
                await service.update_by_id(1, AuditUpdate(detail=changed))

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
    async def test_count(self, migrate, init_audit, factory_with_session):
        async with factory_with_session(AuditService) as service:
            result = await service.count()
            assert result == 2


# ===================

class DemoKombu(KombuMixin):
    """Demo Kombu mixin."""
    name = 'test'


@pytest.fixture()
def kombu():
    """Fixture kombu."""
    k = DemoKombu()
    yield k
    # k.server_stop()


def test_kombu_mixin_init(kombu):
    """Test init kombu mixin."""
    assert kombu.connect.info()


def test_init_kombu_mixin_exception():
    """Test raise exception when init kombu mixin."""
    with pytest.raises(Exception):
        KombuMixin()


@pytest.mark.asyncio
async def test_kombu_mixin_publish_consume(kombu, server_start_signal):
    """Test publish a record to consume."""
    queue_name = 'test'
    length = 2
    for _ in range(length):
        kombu.publish(
            queue_name=queue_name,
            routing_key=queue_name,
            body={'test': 'test111'}
        )
    consume_count = 0

    def callback(_body: Dict, message: Message):  # pyint: disable=unused=argument
        nonlocal consume_count
        consume_count += 1
        message.ack()

    await kombu.consume(
        queue_name=queue_name,
        routing_key=queue_name,
        limit=2,
        # timeout=5,
        register_callbacks=[callback]
    )
    assert consume_count == length
