"""Test job dao"""
import pytest
from sqlalchemy import select

from crawlerstack_spiderkeeper.dao.job import JobDAO
from crawlerstack_spiderkeeper.db.models import Job, Task


@pytest.fixture()
async def dao(dao_factory):
    async with dao_factory(JobDAO) as job_dao:
        yield job_dao


@pytest.mark.parametrize(
    'exist',
    [True, False]
)
@pytest.mark.asyncio
async def test_job_state(init_task, session, dao, exist):
    """test job_state"""
    if exist:
        obj = await session.scalar(select(Job))
        status = await dao.status(pk=obj.id)
        task = await session.scalar(select(Task))
        assert task.status == status.value
    else:
        status = await dao.status(pk=100)
        assert not status
