import pytest

from crawlerstack_spiderkeeper.dao import project_dao
from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.schemas.project import (ProjectCreate,
                                                       ProjectUpdate)
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist


def test_get(init_project, session):
    exist_obj = session.query(Project).first()
    obj = project_dao.get(exist_obj.id)
    assert obj
    assert exist_obj.id == obj.id


def test_get_not_exist(migrate):
    with pytest.raises(ObjectDoesNotExist):
        project_dao.get(1)


def test_get_multi_not_exist(migrate):
    objs = project_dao.get_multi()
    assert not objs


def test_get_multi(init_project, session):
    objs = project_dao.get_multi()
    assert len(objs) == session.query(Project).count()


def test_create(migrate):
    obj = project_dao.create(obj_in=ProjectCreate(name='xx', slug='xx'))
    assert obj.id == 1


def test_create_exception(init_project, session):
    """
    MySQLdb._exceptions.IntegrityError: (1062, "Duplicate entry 'test1' for key 'slug'")
    :param init_project:
    :param session:
    :return:
    """
    with pytest.raises(Exception):
        exist_obj = session.query(Project).first()
        project_dao.create(obj_in=ProjectCreate(name=exist_obj.name, slug=exist_obj.slug))


def test_update(init_project, session):
    exist_obj = session.query(Project).first()
    before_name = exist_obj.name
    changed_name = 'test_update'
    obj = project_dao.update(db_obj=project_dao.get(pk=exist_obj.id), obj_in=ProjectUpdate(name=changed_name))
    assert obj.name == changed_name
    assert before_name != obj.name


def test_update_use_dict_data(init_project, session):
    exist_obj = session.query(Project).first()
    before_name = exist_obj.name
    changed_name = 'test_update'
    obj = project_dao.update(db_obj=project_dao.get(pk=exist_obj.id), obj_in={'name': changed_name})
    assert obj.name == changed_name
    assert before_name != obj.name


def test_update_by_id(init_project, session):
    exist_obj = session.query(Project).first()
    before_name = exist_obj.name
    changed_name = 'test_update'
    obj = project_dao.update_by_id(pk=exist_obj.id, obj_in=ProjectUpdate(name=changed_name))
    assert obj.name == changed_name
    assert before_name != obj.name


def test_update_by_id_obj_not_exist(migrate):
    with pytest.raises(ObjectDoesNotExist):
        project_dao.update_by_id(pk=1, obj_in=ProjectUpdate(name='x'))


def test_delete(init_project, session):
    exist_obj = session.query(Project).first()
    count = session.query(Project).count()
    project_dao.delete(db_obj=project_dao.get(pk=exist_obj.id))
    assert project_dao.count() == count - 1


def test_delete_by_id(init_project, session):
    exist_obj = session.query(Project).first()
    count = session.query(Project).count()
    project_dao.delete_by_id(pk=exist_obj.id)
    assert project_dao.count() == count - 1


def test_delete_by_id_obj_not_exist(migrate):
    with pytest.raises(ObjectDoesNotExist):
        project_dao.delete_by_id(pk=1)


def test_count(migrate):
    assert not project_dao.count()
