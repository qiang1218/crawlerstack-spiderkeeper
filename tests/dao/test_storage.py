"""Test storage dao"""
import pytest
from sqlalchemy import func, select

from crawlerstack_spiderkeeper.dao.storage import StorageDAO
from crawlerstack_spiderkeeper.db.models import Storage
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist
from crawlerstack_spiderkeeper.utils.status import Status


@pytest.fixture()
async def dao(dao_factory):
    async with dao_factory(StorageDAO) as _dao:
        yield _dao


@pytest.mark.asyncio
async def test_increase_storage_count(init_storage, dao, session):
    """test increase_storage_count"""
    before = await session.scalar(select(Storage))
    after = await dao.increase_storage_count(pk=before.id)
    assert after.count == before.count + 1


@pytest.mark.asyncio
async def test_running_storage(init_storage, dao, session):
    """test running_storage"""
    objs = await dao.running_storage()
    stmt = select(
        func.count()
    ).select_from(Storage).filter(
        Storage.status == Status.RUNNING.value
    )
    total = await session.scalar(stmt)
    assert len(objs) == total


@pytest.mark.asyncio
async def test_running_storage_error(dao, session):
    """test running_storage"""
    with pytest.raises(ObjectDoesNotExist):
        await dao.running_storage()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'exist',
    [True, False]
)
async def test_get_by_job_id(init_storage, dao, session, exist):
    """test get by job id."""
    if exist:
        storage = await session.get(Storage, 1)
        res = await dao.get_by_job_id(storage.job_id)
        assert res
    else:
        with pytest.raises(ObjectDoesNotExist):
            await dao.get_by_job_id(100)
