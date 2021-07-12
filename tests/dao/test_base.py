"""
Test base dao.
"""
import pytest
from sqlalchemy import select
from sqlalchemy.sql.functions import count, func

from crawlerstack_spiderkeeper.dao import AuditDAO
from crawlerstack_spiderkeeper.db.models import Audit
from crawlerstack_spiderkeeper.schemas.audit import AuditCreate, AuditUpdate
from crawlerstack_spiderkeeper.utils.exceptions import (ObjectDoesNotExist,
                                                        SpiderkeeperError)


@pytest.fixture()
def dao():
    """dao fixture"""
    yield AuditDAO()


@pytest.mark.asyncio
async def test_get(init_audit, session, dao):
    """Test get a object."""
    exist_obj = await session.scalar(select(Audit))
    obj = await dao.get(exist_obj.id)
    assert obj
    assert exist_obj.id == obj.id


@pytest.mark.asyncio
async def test_get_not_exist(migrate, dao):
    """Test get not exist object."""
    with pytest.raises(ObjectDoesNotExist):
        await dao.get(1)


@pytest.mark.asyncio
async def test_get_multi_not_exist(migrate, dao):
    """Test get multi not exist objects."""
    objs = await dao.get_multi()
    assert not objs


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ['order', 'sort', 'expect_value'],
    [
        (None, None, 'gt'),
        (None, None, 'gt'),
        # ('DESC', None, 'gt'),
        # ('ASC', None, 'lt'),
        # (None, 'datetime', 'gt'),
        # (None, 'foo', SpiderkeeperError),
    ]
)
async def test_get_multi(init_audit, session, dao, order, sort, expect_value):
    """Test get multi object."""
    kwargs = {}
    # if order:
    #     kwargs.setdefault('order', order)
    # if sort:
    #     kwargs.setdefault('sort', sort)
    # if expect_value is SpiderkeeperError:
    #     with pytest.raises(SpiderkeeperError):
    #         await dao.get_multi(**kwargs)
    # else:
    #     objs = await dao.get_multi(**kwargs)
    #     stmt = select(func.count()).select_from(Audit)
    #     assert len(objs) == await session.scalar(stmt)
    #     # if expect_value == 'gt':
    #     #     assert objs[0].id > objs[1].id
    #     # elif expect_value == 'lt':
    #     #     assert objs[0].id < objs[1].id
    objs = await dao.get_multi(**kwargs)


def test_create(migrate, dao):
    """Test create a object."""
    obj = dao.create(
        obj_in=AuditCreate(url='https://example.com', method='GET', client='0.0.0.0', detail='foo')
    )
    assert obj.id == 1


@pytest.mark.parametrize(
    'is_dict',
    [True, False]
)
def test_update(init_audit, session, dao, is_dict):
    """Test update a object"""

    exist_obj = session.query(Audit).first()
    before = exist_obj.detail
    changed = f'updated_{before}'
    obj_in = {'detail': changed}
    if not is_dict:
        obj_in = AuditUpdate(**obj_in)
    obj = dao.update(
        db_obj=dao.get(pk=exist_obj.id),
        obj_in=obj_in,
    )
    assert obj.detail == changed
    assert before != obj.detail


@pytest.mark.parametrize(
    'exist',
    [True, False]
)
def test_update_by_id(init_audit, session, dao, exist):
    """Test update a object by id."""
    if exist:
        exist_obj = session.query(Audit).first()
        before = exist_obj.detail
        changed = f'changed_{before}'
        obj = dao.update_by_id(pk=exist_obj.id, obj_in={'detail': changed})
        assert obj.detail == changed
        assert before != obj.detail
    else:
        with pytest.raises(ObjectDoesNotExist):
            dao.update_by_id(pk=500, obj_in={})


def test_delete(init_audit, session, dao):
    """Test delete a object."""
    exist_obj = session.query(Audit).first()
    count = session.query(Audit).count()
    dao.delete(db_obj=dao.get(exist_obj.id))
    assert dao.count() == count - 1


@pytest.mark.parametrize(
    'exist',
    [True, False]
)
def test_delete_by_id(init_audit, session, dao, exist):
    """Test delete a object by id."""
    if exist:
        exist_obj = session.query(Audit).first()
        count = session.query(Audit).count()
        dao.delete_by_id(pk=exist_obj.id)
        assert dao.count() == count - 1
    else:
        with pytest.raises(ObjectDoesNotExist):
            dao.delete_by_id(pk=100)


def test_delete_by_id_obj_not_exist(migrate, dao):
    """Delete a not exist object by id."""
    with pytest.raises(ObjectDoesNotExist):
        dao.delete_by_id(pk=1)


def test_count(migrate, dao):
    """Test count objects."""
    assert not dao.count()
