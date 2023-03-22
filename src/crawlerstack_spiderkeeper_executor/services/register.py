"""register"""
import asyncio
import functools
import logging
from typing import Any

from crawlerstack_spiderkeeper_executor.executor import executor_factory
from crawlerstack_spiderkeeper_executor.utils import SingletonMeta
from crawlerstack_spiderkeeper_executor.utils.request import RequestWithHttpx
from crawlerstack_spiderkeeper_executor.utils.status import Status

logger = logging.getLogger(__name__)


class RegisterService(metaclass=SingletonMeta):
    """Register service"""

    _server_running = None

    def __init__(self, settings):
        """
        init
        :param settings:
        """
        self.settings = settings
        self.executor_cls = executor_factory()
        self.local_url = self.settings.LOCAL_URL
        self.executor_type = self.settings.EXECUTOR_TYPE
        self.executor_name = self.settings.EXECUTOR_NAME
        self.executor_selector = self.settings.EXECUTOR_SELECTOR
        self.heartbeat_interval = self.settings.HEARTBEAT_INTERVAL
        self.heartbeat_timeout = self.settings.HEARTBEAT_TIMEOUT
        self.heartbeat_url = self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_HEARTBEATS_SUFFIX
        self.register_url = self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_EXECUTOR_CREATE_SUFFIX
        self.heartbeat_task = None
        self.heartbeat_retry_count = 0
        self.exist = False

    @property
    def executor(self):
        """executor"""
        return self.executor_cls(self.settings)

    @property
    def server_running(self) -> bool:
        """server running"""
        return self._server_running

    async def server_start(self, **_):
        """server start"""
        if self._server_running is None:
            self._server_running = True

    @property
    def request_session(self):
        """request session"""
        return RequestWithHttpx()

    async def register(self) -> int:
        """
        register
        :return:
        """
        resp = await self.request_session.request('POST', self.register_url, json=self.register_params)
        executor_id = resp.get('data', {}).get('id')
        return executor_id

    @property
    def register_params(self) -> dict:
        """
        register params
        :return:
        """
        return {'name': self.executor_name,
                'selector': self.executor_selector,
                'url': self.local_url,
                'type': self.executor_type}

    async def heartbeat_params(self):
        """
        heartbeat params
        :return:
        """
        resource_view = await self.resource_view()
        resource_view.setdefault('status', Status.ONLINE.value)
        return resource_view

    async def resource_view(self) -> dict:
        """
        resource view
        :return:
        """
        # 添加资源的获取，主要为当前节点的任务个数
        task_count = await self.executor.get()
        # TODO: 后续实现, 方法为实例方法
        return {'memory': 0, 'cpu': 100, 'task_count': len(task_count)}

    async def _heartbeat(self, executor_id: int):
        """
        heartbeat
        :param executor_id:
        :return:
        """
        # 上报心跳和系统资源情况
        while True:
            logger.info('Heartbeat executor_id is %s, next heartbeat is %s seconds later', executor_id,
                        self.heartbeat_interval)
            if not self.server_running:
                break

            if self.heartbeat_interval > self.heartbeat_timeout:
                break
            req_data = await self.heartbeat_params()
            resp = await self.request_session.request('POST', self.heartbeat_url % executor_id,
                                                      json=req_data,
                                                      timeout=5)
            if not resp:
                self.heartbeat_interval += self.settings.HEARTBEAT_INTERVAL
                self.heartbeat_retry_count += 1
            else:
                self.heartbeat_interval = self.settings.HEARTBEAT_INTERVAL
                self.heartbeat_retry_count = 0
            await asyncio.sleep(self.heartbeat_interval)

        self.exist = True

    async def heartbeat(self, executor_id: int) -> Any:
        """heartbeat"""
        task = functools.partial(self._heartbeat, executor_id=executor_id)
        self.heartbeat_task = asyncio.create_task(task())

    async def server_stop(self, **_):
        """server stop"""
        self._server_running = False
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel('server stop!')
