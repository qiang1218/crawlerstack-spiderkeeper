"""
Test base service.
"""
from typing import Dict

import pytest
from kombu import Message
from pydantic import ValidationError

from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.schemas.project import (ProjectCreate,
                                                       ProjectUpdate)
from crawlerstack_spiderkeeper.services import project_service
from crawlerstack_spiderkeeper.services.base import KombuMixin
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist


class TestBaseService:
    """Test base service."""

    @pytest.mark.asyncio
    async def test_get_multi_return_no_result(self, migrate):
        """Test no object when get multi."""
        objs = await project_service.get_multi()
        assert objs == []

    @pytest.mark.asyncio
    async def test_get_multi(self, init_project, session):
        """Test get multi object."""
        objs = await project_service.get_multi()
        assert len(objs) == session.query(Project).count()

    @pytest.mark.asyncio
    async def test_get(self, init_project, session):
        """Test get a object."""
        exist_obj = session.query(Project).first()
        obj = await project_service.get(exist_obj.id)
        assert obj.id == exist_obj.id

    @pytest.mark.asyncio
    async def test_get_return_no_result(self, migrate):
        """Test get a not exist object."""
        with pytest.raises(ObjectDoesNotExist):
            await project_service.get(1)

    @pytest.mark.asyncio
    async def test_create(self, migrate):
        """Test create a object."""
        obj = await project_service.create(obj_in=ProjectCreate(name='foo', slug='foo'))
        assert obj
        assert isinstance(obj, Project)

    # @pytest.mark.asyncio
    # async def test_create_obj_exist(self, init_project, session):
    #     """Test create a exist object."""
    #     # from MySQLdb._exceptions import IntegrityError
    #     # from sqlalchemy.exc import IntegrityError
    #     with pytest.raises(Exception):
    #         exist_obj = session.query(Project).first()
    #         await project_service.create(
    #             obj_in=ProjectCreate(name=exist_obj.name, slug=exist_obj.slug)
    #         )

    @pytest.mark.asyncio
    async def test_create_exception(self):
        """Test raise exception when create a object."""
        with pytest.raises(ValidationError):
            await project_service.create(obj_in=ProjectCreate(name='foo'))

    @pytest.mark.asyncio
    async def test_update(self, init_project, session):
        """Test update a object."""
        exist_obj = session.query(Project).first()
        changed_name = 'test_update'
        obj = await project_service.update(exist_obj.id, ProjectUpdate(name=changed_name))
        assert exist_obj.name != obj.name

    @pytest.mark.asyncio
    async def test_update_obj_not_exist(self, migrate):
        """Test update a not exist object."""
        with pytest.raises(ObjectDoesNotExist):
            changed_name = 'test_update'
            await project_service.update(1, ProjectUpdate(name=changed_name))

    @pytest.mark.asyncio
    async def test_delete(self, init_project, session):
        """Test delete a object."""
        count = session.query(Project).count()
        obj = session.query(Project).first()
        await project_service.delete(pk=obj.id)
        assert count - 1 == session.query(Project).count()

    @pytest.mark.asyncio
    async def test_delete_no_exist(self, migrate):
        """Test delete a not exist object."""
        with pytest.raises(ObjectDoesNotExist):
            await project_service.delete(pk=1)


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
