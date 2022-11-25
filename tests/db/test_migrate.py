"""
Tests.
"""
import pytest
from sqlalchemy import inspect, select

from crawlerstack_spiderkeeper.db.models import Audit


@pytest.mark.asyncio
async def test_migrate(session):
    """
    Test migrate.
    :param session:
    :return:
    """
    async with session.bind.connect() as connection:
        table_names = await connection.run_sync(session.bind.dialect.get_table_names)
        assert table_names
        assert 'audit' in table_names


@pytest.mark.asyncio
async def test_db(session, init_audit, init_job):
    """
    Test database connect.
    :param session:
    :param init_audit:
    :param init_job:
    :return:
    """
    obj = await session.scalar(select(Audit))
    assert obj
    assert isinstance(obj, Audit)
