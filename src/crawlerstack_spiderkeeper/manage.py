"""
Manager.
"""
import asyncio
import logging
import signal as system_signal

from crawlerstack_spiderkeeper.api import Api
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils.log import configure_logging

HANDLED_SIGNALS = (
    system_signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    system_signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


class SpiderKeeper:
    """Spiderkeeper manager"""

    def __init__(self, settings):
        configure_logging()
        self.__should_exit = False
        self.__force_exit = False
        self.__loop = asyncio.get_event_loop()

        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self.settings = settings

        self.api = Api(host=self.settings.HOST, port=self.settings.PORT, debug=self.settings.DEBUG)

    async def start_api(self):
        """Start api"""
        self.api.init()
        await self.api.start_server()

    def run(self):
        """Run"""
        self.__loop.create_task(server_start.send())
        self.__loop.run_until_complete(self.start_api())
        self.__loop.create_task(server_stop.send())
        self.__loop.stop()
