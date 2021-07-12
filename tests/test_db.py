"""
Tests.
"""
import pytest
from sqlalchemy import select

from crawlerstack_spiderkeeper.db.models import Audit


@pytest.mark.asyncio
async def test_migrate(session):
    """
    Test migrate.
    :param session:
    :return:
    """
    async with session.bind.connect() as connection:
        tables_name = await connection.run_sync(session.bind.dialect.get_table_names)
        assert tables_name
        assert 'audit' in tables_name


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
