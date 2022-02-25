"""Test task dao"""
import pytest
from sqlalchemy import func, select

from crawlerstack_spiderkeeper.dao.task import TaskDAO
from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.utils.status import Status


@pytest.fixture()
async def dao(dao_factory):
    async with dao_factory(TaskDAO) as _dao:
        yield _dao


@pytest.mark.asyncio
async def test_get_running(init_task, session, dao):
    """test get_running"""
    tasks = await dao.get_running()
    stmt = select(func.count()).select_from(Task).filter(Task.status == Status.RUNNING.value)
    assert len(tasks) == await session.scalar(stmt)
    tasks = await dao.get_running(job_id=100)
    assert not tasks


@pytest.mark.asyncio
async def test_count_running_task(init_task, session, dao):
    """test count_running_task"""
    count = await dao.count_running_task()
    stmt = select(func.count()).select_from(Task).filter(Task.status == Status.RUNNING.value)
    assert count == await session.scalar(stmt)

    count = await dao.count_running_task(job_id=100)
    assert not count


@pytest.mark.asyncio
async def test_increase_item_count(init_task, session, dao):
    """test increase_item_count"""
    before = await session.scalar(select(Task))
    after = await dao.increase_item_count(before.id)
    assert after.item_count == before.item_count + 1
