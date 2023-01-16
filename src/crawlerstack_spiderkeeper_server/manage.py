"""
Manager.
"""
import asyncio
import logging
import signal as system_signal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from crawlerstack_spiderkeeper_server.rest_api import RestAPI
from crawlerstack_spiderkeeper_server.signals import server_start, server_stop
from crawlerstack_spiderkeeper_server.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper_server.utils.log import configure_logging

HANDLED_SIGNALS = (
    system_signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    system_signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)

logger = logging.getLogger(__name__)


class SpiderKeeperServer:
    """Spiderkeeper manager"""

    def __init__(self, settings):
        configure_logging()

        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[AsyncSession] = None

        self.settings = settings

        self._rest_api = RestAPI(
            host=self.settings.HOST,
            port=self.settings.PORT,
            debug=self.settings.DEBUG,
            db_url=self.settings.DATABASE
        )
        self.should_exit = False
        self.force_exit = True

    @property
    def rest_api(self):
        """rest api"""
        return self._rest_api

    async def start(self):
        """Start api"""
        self.rest_api.init()
        await server_start.send()
        logger.debug('Spiderkeeper server started')

    async def run(self):
        """Run"""
        try:
            await self.rest_api.start()
            self.install_signal_handlers()
            await self.start()
            while not self.should_exit:
                # 暂时不做任何处理。
                await asyncio.sleep(0.001)
        except SpiderkeeperError as ex:
            logging.exception(ex)
        finally:
            await self.stop()

    async def stop(self):
        """Stop spiderkeeper"""
        await server_stop.send()
        await self.rest_api.stop()

    def install_signal_handlers(self) -> None:
        """
        覆盖信号处理函数，捕获 Ctrl-C 信号，以便于优雅处理强制结束逻辑。

        :return:
        """
        loop = asyncio.get_event_loop()

        try:
            for sig in HANDLED_SIGNALS:
                loop.add_signal_handler(sig, self.handle_exit, sig, None)
        except NotImplementedError:  # pragma: no cover
            # Windows
            for sig in HANDLED_SIGNALS:
                system_signal.signal(sig, self.handle_exit)

    def handle_exit(self, _sig, _frame):
        """
        处理退出逻辑。

        :param _sig:
        :param _frame:
        :return:
        """
        if self.should_exit:
            self.force_exit = True
        else:
            self.should_exit = True
