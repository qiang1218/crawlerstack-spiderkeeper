from collections import Callable
from typing import Type, AsyncContextManager
import contextlib

import pytest

from crawlerstack_spiderkeeper.dao.base import BaseDAO


@pytest.fixture()
def dao_factory(spiderkeeper) -> Callable[..., AsyncContextManager]:
    @contextlib.asynccontextmanager
    async def factory(dao_kls: Type[BaseDAO]):
        async with spiderkeeper.db.session() as session:
            async with session.begin():
                yield dao_kls(session)

    return factory
