"""base"""
import asyncio
import functools
import json
import logging
from asyncio import AbstractEventLoop

import amqp.exceptions
from kombu import Message

from crawlerstack_spiderkeeper_server.collector.utils import Kombu
from crawlerstack_spiderkeeper_server.utils import SingletonMeta

# 提供消息队列的基本操作，用来进行日志，指标，数据的收集，由各子服务实现对应功能
logger = logging.getLogger(__name__)


class BaseTask:
    """Base task"""
    NAME = 'BASE'
    kombu = Kombu()

    _task: asyncio.Task | None = None

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
        # 系统启动后开启监控数据消费任务
        loop = asyncio.get_running_loop()

        self._task = loop.create_task(self.kombu.consume(
            queue_name=self.queue_name,
            routing_key=self.routing_key,
            exchange_name=self.exchange_name,
            register_callbacks=[functools.partial(self.consuming, loop=loop)],
        ))
        logger.debug('Start consuming data from kombu.')

    async def stop(self, **_):
        """
        Stop server
        :return:
        """
        if self._task and not self._task.done():
            self._task.cancel()
            logger.debug('Cancel background task.')
        logger.info('Stopped background task, name: %s', self.NAME)

    async def callback(self, body: dict):
        """Callback"""
        raise NotImplementedError

    def consuming(self, body: str, message: Message, loop: AbstractEventLoop):
        """consume on response"""
        body = json.loads(body)
        task = asyncio.run_coroutine_threadsafe(self.callback(body), loop)
        task.add_done_callback(message.ack)  # 手动 ack


class StorageBaseTask(metaclass=SingletonMeta):
    """Storage base task"""
    NAME: str
    kombu = Kombu()
    _storage_background_tasks: dict[str, asyncio.Task] = {}
    dead_letter_queue = 'spiderkeeper_dead_queue'

    def routing_key(self, task_name: str):
        """Routing key."""
        return self.background_task_id(task_name)

    def queue_name(self, task_name: str):
        """Queue name"""
        return self.background_task_id(task_name)

    @property
    def exchange_name(self):
        """Exchange name."""
        return self.NAME

    def background_task_id(self, task_name: str) -> str:
        """Background task id"""
        return f'{self.NAME}-{task_name}'

    async def start(self, **kwargs):
        """
        Start server
        :return:
        """
        task_name = kwargs.pop('task_name', None)
        if task_name in self._storage_background_tasks:
            logger.warning('Storage task already exist, task name: %s', task_name)
            return
        logger.info('Starting storage task, task name: %s', task_name)
        # 系统启动后开启监控数据消费任务
        loop = asyncio.get_running_loop()

        _task = loop.create_task(self.kombu.consume(
            queue_name=self.queue_name(task_name),
            routing_key=self.routing_key(task_name),
            exchange_name=self.exchange_name,
            register_callbacks=[functools.partial(self.consuming, loop=loop)],
        ))
        self._storage_background_tasks.setdefault(task_name, _task)
        logger.debug('Start consuming data from kombu, task_name: %s', task_name)

    async def stop(self, **_):
        """
        Stop server
        系统退出，仅清除任务
        :return:
        """
        for task_name, _task in self._storage_background_tasks.items():
            if _task and not _task.done():
                self.cancel_consumer(self.queue_name(task_name))
                _task.cancel()
            logger.debug('Cancel storage task, task name: %s', task_name)
        logger.info('Stopped storage task, name: %s', self.NAME)

    def cancel_consumer(self, queue_name: str):
        """
        Cancel consumer by queue name
        :param queue_name:
        :return:
        """
        self.kombu.cancel_consumer(queue_name)

    def delete_queue(self, queue_name: str):
        """
        Delete queue by queue name
        :param queue_name:
        :return:
        """
        self.kombu.delete_queue(queue_name, if_unused=True, if_empty=True)

    def clear(self, **kwargs):
        """
        Clear task
        手动清理任务，说明任务已经完成，队列可以清除
        :param kwargs:
        :return:
        """
        task_name = kwargs.pop('task_name')
        _task = self._storage_background_tasks.pop(task_name)
        if _task and _task.done():
            # 取消当前信道的消费者
            self.cancel_consumer(self.queue_name(task_name))
            _task.cancel()
            logger.debug('Cancel storage task, task name: %s', task_name)

    async def terminate(self, **kwargs):
        """
        Terminate a storage task
        :param kwargs:
        :return:
        """
        task_name = kwargs.pop('task_name')
        self.clear(task_name=task_name)
        await asyncio.sleep(0.1)
        queue_name = self.queue_name(task_name)
        self.delete_queue(queue_name)
        logger.debug('Clear queue, name: %s', queue_name)

    async def queue_count(self, task_name: str, **kwargs) -> int:
        """Queue count"""
        try:
            return self.kombu.queue_declare(self.queue_name(task_name), **kwargs).message_count
        except amqp.exceptions.NotFound:
            return -1

    @staticmethod
    async def callback(body: dict):
        """
        消费数据，并将数据写入数据目标库中。
        :param body:
        :return:
        """
        raise NotImplementedError

    async def _consuming(self, body: dict, message: Message, loop: AbstractEventLoop):
        task = loop.create_task(self.callback(body))
        try:
            await task
        except Exception as ex:
            logger.warning('Consume failed, exception info: %s, try reject,', ex)
            message.reject()
            body.update({'exception': str(ex)})
            await self.kombu.publish(self.dead_letter_queue, self.dead_letter_queue, self.dead_letter_queue,
                                     json.dumps(body))
            await asyncio.sleep(3)
        else:
            message.ack()

    def consuming(self, body: str, message: Message, loop: AbstractEventLoop):
        """consume on response"""
        body = json.loads(body)
        asyncio.run_coroutine_threadsafe(self._consuming(body, message, loop), loop)
