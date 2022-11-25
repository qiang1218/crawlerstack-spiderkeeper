import pytest
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncSession

from crawlerstack_spiderkeeper.db import Database, session_provider
from crawlerstack_spiderkeeper.db.models import Audit


def show_table_sql(name: str) -> str:
    """
    由于 sqlite 没有 `SHOW TABLES` 命令，所以使用此方法进行适配。

    通过查看 `inspector.get_table_names()` 执行的实际命令，发现在查询 sqlite 的时候
    使用的实际 SQL 语言是  `SELECT name FROM sqlite_master WHERE type='table' ORDER BY name`
    """
    if name == 'sqlite':
        return "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    return 'SHOW TABLES'


@pytest.mark.asyncio
async def test_database():
    async with Database() as d1:
        async with Database() as d2:
            assert d1 == d2
            assert d1.engine == d2.engine


@pytest.mark.asyncio
async def test_engine():
    async with Database() as db:
        async with db.engine.connect() as connector:
            def get_table_names(conn: Connection):
                inspector = inspect(conn)
                return inspector.get_table_names()

            table_names = await connector.run_sync(get_table_names)

            assert table_names
            assert 'project' in table_names


@pytest.mark.asyncio
async def test_session(migrate):
    async with Database() as db:
        async with db.session() as session:
            result = await session.scalar(text(show_table_sql(db.engine.name)))
            assert result


@pytest.mark.asyncio
async def test_session_provider_1(migrate, spiderkeeper):
    @session_provider
    async def _func(session: AsyncSession):
        return await session.scalar(text(show_table_sql(session.bind.name)))

    assert await _func()

    @session_provider()
    async def _func(session: AsyncSession):
        return await session.scalar(text(show_table_sql(session.bind.name)))

    async with spiderkeeper.db.session() as se:
        assert await _func(se)

    @session_provider()
    async def _func():
        """"""

    with pytest.raises(ValueError):
        assert await _func()


async def add_audit(session: AsyncSession):
    audit = Audit(
        url='https://example.com',
        method='POST',
        client='127.0.0.1:25552',
        detail='foo'
    )
    session.add(audit)


@session_provider(auto_commit=True)
async def add_audit_with_session_provider(session: AsyncSession):
    audit = Audit(
        url='https://example.com',
        method='POST',
        client='127.0.0.1:25552',
        detail='foo'
    )
    session.add(audit)


@session_provider(auto_commit=True)
async def func(session):
    """
    主要为了测试在多层 session_provider 嵌套的情况先
    内层的 session_provider 会不会将外层提供的 session
    关闭，导致后续无法使用。
    :param session:
    :return:
    """
    await add_audit_with_session_provider()
    await add_audit(session)


@pytest.mark.asyncio
async def test_session_provider(migrate, spiderkeeper, session):
    await func()

    res = await session.scalar(text('SELECT COUNT(*) FROM audit'))
    assert res == 2
