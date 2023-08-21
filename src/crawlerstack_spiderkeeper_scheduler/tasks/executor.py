"""check executor task"""
import asyncio
import logging
import time

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
        for executor in executors:
            # 默认3倍心跳的时间作为过期判断,考虑数据库时区和服务的不一致，故添加字段，进行判断
            if executor.expired_time + self.heartbeat_interval * 3 < int(time.time()):
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
