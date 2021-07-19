"""
Test base dao.
"""
import inspect

import pytest
from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.sql.functions import count, func

from crawlerstack_spiderkeeper.dao.audit import AuditDAO
from crawlerstack_spiderkeeper.db.models import Audit
from crawlerstack_spiderkeeper.schemas.audit import AuditCreate, AuditUpdate
from crawlerstack_spiderkeeper.utils.exceptions import (ObjectDoesNotExist,
                                                        SpiderkeeperError)


@pytest.fixture()
async def dao(spiderkeeper):
    """dao fixture"""
    async with spiderkeeper.db.session() as session:
        async with session.begin():
            yield AuditDAO(session)


@pytest.mark.asyncio
async def test_get_by_id(init_audit, session, dao):
    """Test get a object."""
    exist_obj = await session.scalar(select(Audit))
    obj = await dao.get_by_id(exist_obj.id)
    assert obj
    assert exist_obj.id == obj.id


@pytest.mark.asyncio
async def test_get_by_id_not_exist(migrate, dao):
    """Test get not exist object."""
    with pytest.raises(ObjectDoesNotExist):
        await dao.get_by_id(1)


@pytest.mark.asyncio
async def test_get_not_exist(migrate, dao):
    """Test get multi not exist objects."""
    objs = await dao.get()
    assert not objs


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ['sort', 'search', 'expect_value'],
    [
        (None, None, 'lt'),
        (['id'], None, 'lt',),
        (['-id'], None, 'gt'),
        (None, {'detail': 'bar'}, 'gt'),
        (None, {'abc': 'bar'}, InvalidRequestError),
    ]
)
async def test_get(init_audit, session, dao, sort, search, expect_value):
    """Test get multi object."""
    kwargs = {}
    if search:
        kwargs.setdefault('search_fields', search)
    if sort:
        kwargs.setdefault('sorting_fields', sort)
    if inspect.isclass(expect_value) and issubclass(expect_value, Exception):
        with pytest.raises(expect_value):
            await dao.get(**kwargs)
    else:
        objs = await dao.get(**kwargs)
        assert objs

        if len(objs) > 1:

            stmt = select(func.count()).select_from(Audit)
            assert len(objs) == await session.scalar(stmt)
            if expect_value == 'gt':
                assert objs[0].id > objs[1].id
            elif expect_value == 'lt':
                assert objs[0].id < objs[1].id
        else:
            k, v = search.popitem()
            obj = objs[0]
            assert getattr(obj, k) == v


@pytest.mark.asyncio
async def test_create(migrate, spiderkeeper):
    """Test create a object."""
    async with spiderkeeper.db.session() as session:
        async with session.begin():
            dao = AuditDAO(session)
            obj = await dao.create(
                obj_in=AuditCreate(url='https://example.com', method='GET', client='0.0.0.0', detail='foo')
            )
    assert obj.id == 1


@pytest.mark.parametrize(
    'is_dict',
    [True, False]
)
@pytest.mark.asyncio
async def test_update(init_audit, session, dao, is_dict):
    """Test update a object"""

    exist_obj = await session.scalar(select(Audit))
    before = exist_obj.detail
    changed = f'updated_{before}'
    obj_in = {'detail': changed}
    if not is_dict:
        obj_in = AuditUpdate(**obj_in)
    obj = await dao.get_by_id(pk=exist_obj.id)
    obj = await dao.update(
        db_obj=obj,
        obj_in=obj_in,
    )
    assert obj.detail == changed
    assert before != obj.detail


@pytest.mark.parametrize(
    'exist',
    [True, False]
)
@pytest.mark.asyncio
async def test_update_by_id(init_audit, session, dao, exist):
    """Test update a object by id."""
    if exist:
        exist_obj = await session.scalar(select(Audit))
        before = exist_obj.detail
        changed = f'changed_{before}'
        obj = await dao.update_by_id(pk=exist_obj.id, obj_in={'detail': changed})
        assert obj.detail == changed
        assert before != obj.detail
    else:
        with pytest.raises(ObjectDoesNotExist):
            await dao.update_by_id(pk=500, obj_in={})


@pytest.mark.asyncio
async def test_delete(init_audit, session, dao):
    """Test delete a object."""
    exist_obj = await session.scalar(select(Audit))
    total = await session.scalar(select(func.count()).select_from(Audit))
    obj = await dao.get_by_id(exist_obj.id)
    await dao.delete(db_obj=obj)
    assert await dao.count() == total - 1


@pytest.mark.parametrize(
    'exist',
    [True, False]
)
@pytest.mark.asyncio
async def test_delete_by_id(init_audit, session, dao, exist):
    """Test delete a object by id."""
    if exist:
        exist_obj = await session.scalar(select(Audit))
        total = await session.scalar(select(func.count()).select_from(Audit))
        await dao.delete_by_id(pk=exist_obj.id)
        assert await dao.count() == total - 1
    else:
        with pytest.raises(ObjectDoesNotExist):
            await dao.delete_by_id(pk=100)


@pytest.mark.asyncio
async def test_delete_by_id_obj_not_exist(migrate, dao):
    """Delete a not exist object by id."""
    with pytest.raises(ObjectDoesNotExist):
        await dao.delete_by_id(pk=1)


@pytest.mark.asyncio
async def test_count(migrate, dao):
    """Test count objects."""
    total = await dao.count()
    assert total == 0
