"""Test server dao"""
import pytest
from sqlalchemy import select

from crawlerstack_spiderkeeper.dao.server import  ServerDAO
from crawlerstack_spiderkeeper.db.models import Job


@pytest.fixture()
async def dao(dao_factory):
    async with dao_factory(ServerDAO) as _dao:
        yield _dao


@pytest.mark.asyncio
async def test_get_server_by_job_id(init_job, session, dao):
    """test get_server_by_job_id"""
    job = await session.scalar(select(Job))
    server = await dao.get_server_by_job_id(job_id=job.id)
    assert job.server_id == server.id
