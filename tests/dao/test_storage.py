"""Test storage dao"""
import pytest
from sqlalchemy import select, func

from crawlerstack_spiderkeeper.dao.storage import StorageDAO
from crawlerstack_spiderkeeper.db.models import Storage
from crawlerstack_spiderkeeper.utils.states import States


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
    stmt = select(func.count()).select_from(Storage).filter(Storage.state == States.RUNNING.value)
    total = await session.scalar(stmt)
    assert len(objs) == total
