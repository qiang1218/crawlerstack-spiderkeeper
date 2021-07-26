"""
Service API
"""
import asyncio
from asyncio import Task
from typing import Optional

from fastapi import FastAPI
from uvicorn import Config, Server

from crawlerstack_spiderkeeper.db import Database
from crawlerstack_spiderkeeper.rest_api.middlewares import init_middleware
from crawlerstack_spiderkeeper.rest_api.routers import init_router


class RestAPI:
    """
    Service API
    """

    def __init__(
            self,
            db: Database,
            port: Optional[int] = 8080,
            host: Optional[str] = '127.0.0.1',
            debug=False,
            name: Optional[str] = __name__,
            reload: Optional[bool] = False,

    ):
        self.name = name
        self.host = host
        self.port = port
        self.debug = debug
        self.reload = reload

        self._app = FastAPI(
            title="SpiderKeeper",
            version="2.0",
            db=db,
        )

        uvicorn_config = Config(self.app)
        self._uvicorn_server = Server(uvicorn_config)
        self._server_task: Optional[Task] = None

    @property
    def app(self) -> FastAPI:
        return self._app

    def init(self):
        """
        初始化 API
        :return:
        """
        # init_middleware(self.app)
        init_router(self.app)

    async def _uvicorn_server_setup(self):
        config = self._uvicorn_server.config
        if not config.loaded:
            config.load()

        self._uvicorn_server.lifespan = config.lifespan_class(config)
        await self._uvicorn_server.startup()

    async def start(self) -> None:
        """"""
        self.init()
        await self._uvicorn_server_setup()

    async def stop(self) -> None:
        """"""
        await self._uvicorn_server.shutdown()

    async def restart(self) -> None:
        """"""
