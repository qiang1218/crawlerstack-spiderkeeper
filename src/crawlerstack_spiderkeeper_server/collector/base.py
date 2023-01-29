"""base"""
import asyncio
import functools
import json
import logging
from asyncio import AbstractEventLoop
from typing import Optional

from kombu import Message

from crawlerstack_spiderkeeper_server.collector.utils import Kombu

# 提供消息队列的基本操作，用来进行日志，指标，数据的收集，由各子服务实现对应功能
logger = logging.getLogger(__name__)


class BaseTask:
    """Base task"""
    NAME = 'BASE'
    kombu = Kombu()

    _task: Optional[asyncio.Task] = None
    _should_stop: asyncio.Future = asyncio.Future()

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

    async def start(self, **_):
        """
        Start server
        :return:
        """
        logger.info('Starting task, name: %s', self.NAME)
        if self._should_stop.done():
            self._should_stop = asyncio.Future()

        # 系统启动后开启监控数据消费任务
        loop = asyncio.get_running_loop()

        self._task = loop.create_task(self.kombu.consume(
            queue_name=self.queue_name,
            routing_key=self.routing_key,
            exchange_name=self.exchange_name,
            register_callbacks=[functools.partial(self.consuming, loop=loop)],
            should_stop=self._should_stop
        ))
        logger.debug('Start consuming data from kombu.')

    async def stop(self, **_):
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
        logger.info('Stopped metric task, name: %s', self.NAME)

    async def callback(self, data: dict):
        """Callback"""
        raise NotImplementedError

    def consuming(self, body: str, message: Message, loop: AbstractEventLoop):
        """consume on response"""
        body = json.loads(body)
        task = asyncio.run_coroutine_threadsafe(self.callback(body), loop)
        task.add_done_callback(message.ack)  # 手动 ack
