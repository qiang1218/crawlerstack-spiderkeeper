"""
Manager.
"""
import logging
import signal as system_signal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from crawlerstack_spiderkeeper.rest_api import RestAPI
from crawlerstack_spiderkeeper.db import init_db, Database
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
            await self.start()
        except SpiderkeeperError as ex:
            logging.exception(ex)
        finally:
            await self.stop()

    async def stop(self):
        """Stop spiderkeeper"""
        # await server_stop.send()
        await self.rest_api.stop()
        await self.db.close()
