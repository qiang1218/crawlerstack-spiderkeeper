"""check executor task"""
import asyncio
import logging
from datetime import datetime, timedelta

from fastapi_sa.database import session_ctx

from crawlerstack_spiderkeeper_scheduler.config import settings
from crawlerstack_spiderkeeper_scheduler.services.executor import \
    ExecutorService
from crawlerstack_spiderkeeper_scheduler.utils import SingletonMeta
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    ObjectDoesNotExist
from crawlerstack_spiderkeeper_scheduler.utils.status import Status

logger = logging.getLogger(__name__)


class ExecutorTask(metaclass=SingletonMeta):
    """Executor task"""

    name = 'executor_task'

    task: asyncio.Task | None = None
    heartbeat_interval = settings.HEARTBEAT_INTERVAL

    _server_running = None

    @property
    def server_running(self) -> bool:
        """server running"""
        return self._server_running

    async def server_start(self, **_):
        """server start"""
        if self._server_running is None:
            logger.debug('Change %s.server_running to "True"', self.__class__.name)
            self._server_running = True

    @property
    def executor_service(self):
        """executor service"""
        return ExecutorService()

    async def run(self, **_):
        """
        run executor task
        :return:
        """
        logger.info('Check executor task is running')
        while True:
            if not self._server_running:
                break
            await self._run_wrapper()
            await asyncio.sleep(self.heartbeat_interval * 3)
        logger.info('Check executor task is stopped')

    @session_ctx
    async def _run_wrapper(self):
        """_run wrapper"""
        try:
            executors = await self.executor_service.get(search_fields={'status': Status.ONLINE.value})  # noqa
        except ObjectDoesNotExist:
            # 定时任务添加一次，持续执行
            return
        current_time = datetime.now() + timedelta(seconds=self.heartbeat_interval * 3)
        if executors:
            for executor in executors:
                if executor.update_time < current_time:
                    await asyncio.sleep(1)
                    await self.executor_service.update(executor.id, obj_in={'status': Status.OFFLINE.value})

    async def check_executor_task(self, **_):
        """task"""
        self.task = asyncio.create_task(self.run())

    async def server_stop(self, **_):
        """server stop"""
        logger.debug('Change %s.server_running to "False"', self.__class__.name)
        self._server_running = False
        if self.task and not self.task.done():
            self.task.cancel('server stop!')
