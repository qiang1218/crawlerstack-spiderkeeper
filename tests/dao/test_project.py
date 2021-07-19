"""Test project dao"""
import pytest

from crawlerstack_spiderkeeper.dao.project import ProjectDAO
from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.schemas.project import ProjectCreate


@pytest.fixture()
async def dao(spiderkeeper):
    async with spiderkeeper.db.session() as session:
        async with session.begin():
            yield ProjectDAO(session)


@pytest.mark.asyncio
async def test_create(migrate, dao):
    """Test create"""
    project = await dao.create(
        obj_in=ProjectCreate(name='foo')
    )
    assert isinstance(project, Project)
    assert project
    assert project.name == 'foo'
