"""base"""
import asyncio
import logging
from typing import Any, Optional

from crawlerstack_spiderkeeper_forwarder.forwarder.utils import Kombu

# 提供消息队列的基本操作，用来进行日志，指标，数据的收集，由各子服务实现对应功能
logger = logging.getLogger(__name__)


class BaseTask:
    """Base task"""
    NAME = 'BASE'
    kombu = Kombu()

    _task: Optional[asyncio.Task] = None
    _should_stop: asyncio.Future = None

    @classmethod
    async def start_from_cls(cls, **_kwargs):
        """
        Stop server
        :return:
        """
        obj = cls()
        await obj.start()

    @classmethod
    async def stop_from_cls(cls, **_kwargs):
        """
        Stop server
        :return:
        """
        obj = cls()
        await obj.stop()

    @classmethod
    async def class_object(cls):
        """class object"""
        return cls()

    @property
    def queue_name(self):
        """Queue name."""
        return self.NAME

    @property
    def routing_key(self):
        """Routing key."""
        return self.NAME

    @property
    def exchange_name(self):
        """Exchange name."""
        return self.NAME

    async def publish(self, body: Any):
        """
        Publish message
        :param body:
        :return:
        """
        await self.kombu.publish(
            queue_name=self.queue_name,
            routing_key=self.routing_key,
            exchange_name=self.exchange_name,
            body=body
        )

    async def start(self, **_):
        """
        Start server
        :return:
        """
        logger.info('Starting task, name: %s', self.NAME)
        if self._should_stop.done():
            self._should_stop = asyncio.Future()

    async def stop(self):
        """
        Stop server
        :return:
        """
        if not self._should_stop.done():
            self._should_stop.set_result('Stop')
            await asyncio.sleep(0)
            if self._task and not self._task.done():
                self._task.cancel()
                logger.debug('Cancel metric task.')
        logger.info('Stopped metric task')
