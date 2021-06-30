"""
Service API
"""
from typing import Optional

from fastapi import FastAPI
from uvicorn import Config, Server

from crawlerstack_spiderkeeper.api.middlewares import init_middleware
from crawlerstack_spiderkeeper.api.routers import init_router
from crawlerstack_spiderkeeper.utils.log import init_logging_config


class ApiServer:
    """
    Service API
    """

    def __init__(
            self,
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

        self.app = FastAPI(title="SpiderKeeper", version="2.0")

    def init(self):
        """
        初始化 API
        :return:
        """
        init_middleware(self.app)
        init_router(self.app)

    async def start(self):
        """
        启动服务
        :return:
        """
        server = Server(Config(
            self.app,
            host=self.host,
            port=self.port,
            reload=self.reload,
            debug=self.debug,
            log_config=init_logging_config(),
        ))
        await server.serve()
