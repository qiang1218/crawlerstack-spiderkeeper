"""test base repository"""
import inspect

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import InvalidRequestError

from crawlerstack_spiderkeeper_server.models import Project
from crawlerstack_spiderkeeper_server.repository.project import \
    ProjectRepository
from crawlerstack_spiderkeeper_server.schemas.project import ProjectUpdate
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist


@pytest.fixture()
async def repo():
    """repo fixture"""
    return ProjectRepository()


async def test_get_by_id(init_project, repo, session):
    """Test get a object."""
    exist_obj = await session.scalar(select(Project).where(Project.id == 1))
    obj = await repo.get_by_id(exist_obj.id)
    assert obj
    assert exist_obj.id == obj.id


async def test_get_by_id_not_exist(repo, session):
    """Test get not exist object."""
    with pytest.raises(ObjectDoesNotExist):
        await repo.get_by_id(3)


async def test_get_not_exist(repo, session):
    """Test get not exist object."""
    with pytest.raises(ObjectDoesNotExist):
        await repo.get()


@pytest.mark.parametrize(
    ['sort', 'search', 'expect_value'],
    [
        (None, None, 'lt'),
        (['id'], None, 'lt',),
        (['-id'], None, 'gt'),
        (None, {'name': 'test1'}, 'gt'),
        (None, {'abc': 'bar'}, InvalidRequestError),
    ]
)
async def test_get(init_project, session, repo, sort, search, expect_value):
    """Test get multi object."""
    kwargs = {}
    if search:
        kwargs.setdefault('search_fields', search)
    if sort:
        kwargs.setdefault('sorting_fields', sort)
    if inspect.isclass(expect_value) and issubclass(expect_value, Exception):
        with pytest.raises(expect_value):
            await repo.get(**kwargs)
    else:
        objs = await repo.get(**kwargs)
        assert objs

        if len(objs) > 1:

            stmt = select(func.count()).select_from(Project)
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
async def test_create(repo, session):
    """Test create a object."""
    obj = await repo.create(
        obj_in=Project(name='test1', desc='test1')
    )
    assert obj.id == 1


@pytest.mark.parametrize(
    'is_dict',
    [True, False]
)
@pytest.mark.asyncio
async def test_update(init_project, session, repo, is_dict):
    """Test update a object"""

    exist_obj = await session.scalar(select(Project))
    before = exist_obj.desc
    changed = f'updated_{before}'
    obj_in = {'desc': changed}
    if not is_dict:
        obj_in = ProjectUpdate(**obj_in)
    obj = await repo.get_by_id(pk=exist_obj.id)
    obj = await repo.update(db_obj=obj, obj_in=obj_in, )  # noqa
    assert obj.desc == changed
    assert before != obj.desc


@pytest.mark.parametrize(
    'exist',
    [True, False]
)
@pytest.mark.asyncio
async def test_update_by_id(init_project, session, repo, exist):
    """Test update an object by id."""
    if exist:
        exist_obj = await session.scalar(select(Project))
        before = exist_obj.desc
        changed = f'changed_{before}'
        obj = await repo.update_by_id(pk=exist_obj.id, obj_in={'desc': changed})
        assert obj.desc == changed
        assert before != obj.desc
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.update_by_id(pk=500, obj_in={})


@pytest.mark.asyncio
async def test_delete(init_project, session, repo):
    """Test delete a object."""
    exist_obj = await session.scalar(select(Project))
    total = await session.scalar(select(func.count()).select_from(Project))
    obj = await repo.get_by_id(exist_obj.id)
    await repo.delete(db_obj=obj)  # noqa
    assert await repo.count() == total - 1


@pytest.mark.parametrize(
    'exist',
    [True, False]
)
@pytest.mark.asyncio
async def test_delete_by_id(init_project, session, repo, exist):
    """Test delete a object by id."""
    if exist:
        exist_obj = await session.scalar(select(Project))
        total = await session.scalar(select(func.count()).select_from(Project))
        await repo.delete_by_id(pk=exist_obj.id)
        assert await repo.count() == total - 1
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.delete_by_id(pk=100)


@pytest.mark.asyncio
async def test_delete_by_id_obj_not_exist(repo, session):
    """Delete a not exist object by id."""
    with pytest.raises(ObjectDoesNotExist):
        await repo.delete_by_id(pk=1)


@pytest.mark.asyncio
async def test_count(repo, session):
    """Test count objects."""
    total = await repo.count()
    assert total == 0


@pytest.mark.asyncio
async def test_count_exist(init_project, repo, session):
    """Test count objects."""
    total = await repo.count()
    assert total == 2
