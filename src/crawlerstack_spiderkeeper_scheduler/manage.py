"""
Manager.
"""
import asyncio
import logging
import signal as system_signal
import threading
from pathlib import Path

from alembic import command
from alembic.config import Config

from crawlerstack_spiderkeeper_scheduler.rest_api import RestAPI
from crawlerstack_spiderkeeper_scheduler.services.scheduler import \
    SchedulerServer
from crawlerstack_spiderkeeper_scheduler.signals import (server_start,
                                                         server_stop)
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    SpiderkeeperError
from crawlerstack_spiderkeeper_scheduler.utils.log import configure_logging

HANDLED_SIGNALS = (
    system_signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    system_signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)

logger = logging.getLogger(__name__)


class SpiderKeeperScheduler:
    """Spiderkeeper manager"""

    def __init__(self, settings):
        log_config = configure_logging()

        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.settings = settings

        self._rest_api = RestAPI(
            host=self.settings.HOST,
            port=self.settings.PORT,
            debug=self.settings.DEBUG,
            db_url=self.settings.DATABASE,
            log_config=log_config
        )
        self.should_exit = False
        self.force_exit = True

        self.scheduler = SchedulerServer(self.settings)
        self.executor_task_id = 'executor_task_id'

    @property
    def rest_api(self):
        """rest api"""
        return self._rest_api

    async def start(self):
        """Start api"""
        self.rest_api.init()
        await server_start.send()

    async def start_background_task(self):
        """Start background task"""
        self.scheduler.start()

    async def stop_background_task(self):
        """stop background task"""
        self.scheduler.stop()

    @staticmethod
    def migrate_db():
        """
        Migrates the database
        :return:
        """
        alembic_cfg = Config(Path(Path(__file__).parent, 'alembic/alembic.ini'))
        alembic_cfg.set_main_option("script_location", "crawlerstack_spiderkeeper_scheduler:alembic")
        command.upgrade(alembic_cfg, 'head')

    def auto_migrate(self):
        """Auto migrate"""
        thread = threading.Thread(target=self.migrate_db)
        thread.start()

    async def run(self):
        """Run"""
        try:
            self.install_signal_handlers()
            self.auto_migrate()
            await self.start()
            await self.rest_api.start()
            await self.start_background_task()
            while not self.should_exit:
                # 暂时不做任何处理。
                await asyncio.sleep(0.001)
        except SpiderkeeperError as ex:
            logging.exception(ex)
        finally:
            await self.stop_background_task()
            await self.stop()

    async def stop(self):
        """Stop spiderkeeper"""
        await server_stop.send()
        await asyncio.sleep(0.001)
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
