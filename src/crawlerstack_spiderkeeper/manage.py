"""
Manager.
"""
import logging
import signal as system_signal

from crawlerstack_spiderkeeper.api import ApiServer
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils.log import configure_logging
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError

HANDLED_SIGNALS = (
    system_signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    system_signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


class SpiderKeeper:
    """Spiderkeeper manager"""

    def __init__(self, settings):
        configure_logging()

        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self.settings = settings

        self.api = ApiServer(
            host=self.settings.HOST,
            port=self.settings.PORT,
            debug=self.settings.DEBUG
        )

    async def start(self):
        """Start api"""
        await server_start.send()
        self.api.init()
        await self.api.start()

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
        await server_stop.send()
