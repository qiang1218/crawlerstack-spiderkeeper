"""
Manager.
"""
import asyncio
import logging
import signal as system_signal

from crawlerstack_spiderkeeper_executor.rest_api import RestAPI
from crawlerstack_spiderkeeper_executor.services.register import \
    RegisterService
from crawlerstack_spiderkeeper_executor.signals import (server_start,
                                                        server_stop)
from crawlerstack_spiderkeeper_executor.utils.exceptions import \
    SpiderkeeperError
from crawlerstack_spiderkeeper_executor.utils.log import configure_logging

logger = logging.getLogger(__name__)

HANDLED_SIGNALS = (
    system_signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    system_signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)

EXIST = False


class SpiderKeeperExecutor:
    """Spiderkeeper manager"""

    def __init__(self, settings):
        log_config = configure_logging()

        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.settings = settings

        self._rest_api = RestAPI(
            host=self.settings.HOST,
            port=self.settings.PORT,
            debug=self.settings.DEBUG,
            log_config=log_config,
        )
        self.should_exit = False
        self.force_exit = True
        self.register = RegisterService(self.settings)

    @property
    def rest_api(self):
        """rest api"""
        return self._rest_api

    async def start(self):
        """Start api"""
        logger.info('Starting spiderkeeper executor')
        self.rest_api.init()
        self.register_event()
        await server_start.send()

    async def start_background_task(self):
        """Start background task"""

        executor_id = await self.register.register()
        if executor_id:
            await self.register.heartbeat(executor_id=executor_id)
        else:
            raise SpiderkeeperError('Init register failed!')

    def register_event(self):
        """register event"""
        # 注册事件
        server_start.connect(self.register.server_start)
        server_stop.connect(self.register.server_stop)

    async def run(self):
        """Run"""
        try:
            await self.rest_api.start()
            self.install_signal_handlers()
            await self.start()
            await self.start_background_task()
            while not self.should_exit:
                # 暂时不做任何处理。
                if self.register.exist:
                    break
                await asyncio.sleep(2)
        except SpiderkeeperError as ex:
            logging.exception(ex)
        finally:
            await self.stop()

    async def stop(self):
        """Stop spiderkeeper"""
        logging.info('Stopping spiderkeeper executor')
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
