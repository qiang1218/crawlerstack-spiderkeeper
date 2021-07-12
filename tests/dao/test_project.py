"""Test project dao"""
import pytest

from crawlerstack_spiderkeeper.dao.project import ProjectDAO
from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.schemas.project import ProjectCreate


@pytest.mark.asyncio
async def test_create(session):
    """Test create"""
    dao = ProjectDAO()
    project = await dao.create(
        obj_in=ProjectCreate(name='foo')
    )
    assert isinstance(project, Project)
    assert project
    assert project.name == 'foo'
