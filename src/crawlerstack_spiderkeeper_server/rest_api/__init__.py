"""
Service API
"""
from asyncio import Task
from typing import Any, Dict, Optional, Union

from fastapi import FastAPI
from fastapi_sa.database import db
from uvicorn import Config, Server

from crawlerstack_spiderkeeper_server import __version__
from crawlerstack_spiderkeeper_server.rest_api.handler import \
    init_exception_handler
from crawlerstack_spiderkeeper_server.rest_api.middlewares import \
    init_middleware
from crawlerstack_spiderkeeper_server.rest_api.routers import init_router


class RestAPI:
    """
    Service API
    """

    def __init__(
            self,
            port: Optional[int] = 8080,
            host: Optional[str] = '127.0.0.1',
            debug: Optional[bool] = False,
            db_url: Optional[str] = 'sqlite+aiosqlite:////.local/server.db',
            name: Optional[str] = __name__,
            reload: Optional[bool] = False,
            log_config: Optional[Union[Dict[str, Any], str]] = None,
    ):
        self.name = name
        self.host = host
        self.port = port
        self.debug = debug
        self.db_url = db_url
        self.reload = reload
        self.log_config = log_config

        self._app = FastAPI(
            title="SpiderKeeperServer",
            version=__version__,
        )

        uvicorn_config = Config(self.app, host=self.host, port=self.port, log_config=self.log_config)
        self._uvicorn_server = Server(uvicorn_config)
        self._server_task: Optional[Task] = None

    @property
    def app(self) -> FastAPI:
        """api"""
        return self._app

    def init_db(self):
        """init db"""
        db.init(url=self.db_url, engine_kw={"pool_recycle": 3600})

    def init(self):
        """
        初始化 API
        :return:
        """
        self.init_db()
        init_middleware(self.app)
        init_exception_handler(self.app)
        init_router(self.app)

    async def _uvicorn_server_setup(self):
        config = self._uvicorn_server.config
        if not config.loaded:
            config.load()

        self._uvicorn_server.lifespan = config.lifespan_class(config)
        await self._uvicorn_server.startup()

    async def start(self) -> None:
        """start"""
        await self._uvicorn_server_setup()

    async def stop(self) -> None:
        """stop"""
        # 由于 _uvicorn_server 是在 startup 是初始化 servers 属性的，
        # 所以在测试时，如果不运行 self.start 逻辑， _uvicorn_server.shutdown
        # 会报错
        if hasattr(self._uvicorn_server, 'servers'):
            await self._uvicorn_server.shutdown()

    async def restart(self) -> None:
        """restart"""
