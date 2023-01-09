"""test base service"""
import inspect

import pytest
from sqlalchemy import select, func

from crawlerstack_spiderkeeper_server.models import Project
from crawlerstack_spiderkeeper_server.schemas.project import ProjectSchema, ProjectCreate, ProjectUpdate

from crawlerstack_spiderkeeper_server.services.project import ProjectService
from crawlerstack_spiderkeeper_server.utils.exceptions import ObjectDoesNotExist


class TestEntityService:

    @pytest.fixture()
    def service(self):
        """service fixture"""
        return ProjectService()

    async def test_get_by_id(self, init_project, session, service):
        """test get by id"""
        exist_obj = await session.scalar(select(Project))
        obj = await service.get_by_id(exist_obj.id)
        assert obj.id == exist_obj.id

    async def test_get(self, init_project, session, service):
        """test get"""
        objs = await service.get()
        stmt = select(func.count()).select_from(Project)
        assert len(objs) == await session.scalar(stmt)

    async def test_create(self, session, service):
        """test create"""

        obj_in = ProjectCreate(name="test1", desc="test1")
        obj = await service.create(obj_in=obj_in)
        assert obj
        assert isinstance(obj, ProjectSchema)

        stmt = select(func.count()).select_from(Project)
        assert await session.scalar(stmt) == 1

    @pytest.mark.parametrize(
        'pk, expect_value',
        [
            (1, 'changed_value'),
            (100, ObjectDoesNotExist)
        ]
    )
    async def test_update(self, init_project, session, service, pk, expect_value):
        """test update"""
        changed = 'test_update'
        if inspect.isclass(expect_value):
            with pytest.raises(expect_value):
                await service.update(pk, ProjectUpdate(desc=changed))
        else:
            obj = await service.update(pk, ProjectUpdate(desc=changed))
            assert obj.desc == changed

    @pytest.mark.parametrize(
        'pk, exist',
        [
            (1, True),
            (100, False)
        ]
    )
    async def test_delete(self, init_project, session, service, pk, exist):
        """test delete"""
        if exist:
            stmt = select(func.count()).select_from(Project)
            before_count = await session.scalar(stmt)
            obj = await session.scalar(select(Project))
            await service.delete_by_id(pk=obj.id)
            after_count = await session.scalar(stmt)
            assert before_count - 1 == after_count
        else:
            with pytest.raises(ObjectDoesNotExist):
                await service.delete_by_id(pk=pk)

    async def test_count(self, init_project, session, service):
        """test count"""
        count = await service.count()
        assert count == 2
