"""
Manager.
"""
import asyncio
import logging
import signal
import signal as system_signal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from crawlerstack_spiderkeeper.db import Database, init_db
from crawlerstack_spiderkeeper.rest_api import RestAPI
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper.utils.log import configure_logging

HANDLED_SIGNALS = (
    system_signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    system_signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


class SpiderKeeper:
    """Spiderkeeper manager"""

    def __init__(self, settings):
        configure_logging()

        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[AsyncSession] = None

        self.settings = settings

        self._db = init_db(self.settings)

        self._rest_api = RestAPI(
            db=self.db,
            host=self.settings.HOST,
            port=self.settings.PORT,
            debug=self.settings.DEBUG
        )
        self.should_exit = False
        self.force_exit = True

    @property
    def db(self) -> Database:
        return self._db

    @property
    def rest_api(self):
        return self._rest_api

    async def start(self):
        """Start api"""
        # await server_start.send()
        self.rest_api.init()
        await self.rest_api.start()

    async def run(self):
        """Run"""
        try:
            self.install_signal_handlers()
            await self.start()
            while not self.should_exit:
                """暂时不做任何处理。"""
                await asyncio.sleep(0.001)
        except SpiderkeeperError as ex:
            logging.exception(ex)
        finally:
            await self.stop()

    async def stop(self):
        """Stop spiderkeeper"""
        # await server_stop.send()
        await self.rest_api.stop()
        await self.db.close()

    def install_signal_handlers(self) -> None:
        loop = asyncio.get_event_loop()

        try:
            for sig in HANDLED_SIGNALS:
                loop.add_signal_handler(sig, self.handle_exit, sig, None)
        except NotImplementedError:  # pragma: no cover
            # Windows
            for sig in HANDLED_SIGNALS:
                signal.signal(sig, self.handle_exit)

    def handle_exit(self, sig, frame):
        if self.should_exit:
            self.force_exit = True
        else:
            self.should_exit = True
