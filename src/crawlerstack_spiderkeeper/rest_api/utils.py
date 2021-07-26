from collections import Callable, AsyncGenerator
from typing import Type, TypeVar

from starlette.requests import Request

from crawlerstack_spiderkeeper.services.base import BaseService

RT = TypeVar('RT', bound=BaseService)


def service_depend(service_kls: Type[RT]) -> Callable[[Request], AsyncGenerator[RT, None]]:
    async def get_service(request: Request):
        db = request.app.extra.get('db')
        async with db.scoped_session() as local_session:
            async with local_session.begin():
                yield service_kls(local_session)

    return get_service
