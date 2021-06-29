"""Test project dao"""
from crawlerstack_spiderkeeper.dao import project_dao
from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.schemas.project import ProjectCreate


def test_create(session):
    """Test create"""
    project_dao.create(
        obj_in=ProjectCreate(name='foo')
    )
    assert session.query(Project).count() == 1
