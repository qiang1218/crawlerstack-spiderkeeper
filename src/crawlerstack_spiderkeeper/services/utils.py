"""
utils
"""
import asyncio
import logging
import socket
from itertools import count
from typing import Any, Callable, List, Optional, TypeVar

from kombu import Connection, Consumer, Exchange, Queue, producers

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils import run_in_executor
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError

_T = TypeVar('_T')

logger = logging.getLogger(__name__)

# FIXME pylint W0603
_SERVER_RUNNING = False
_SERVER_STARTED = False


class Kombu:
    """
    Kombu server ，提供队列服务。

    具有单例性质。
    """
    NAME: str

    _connect = None

    @property
    def server_running(self):
        global _SERVER_RUNNING
        return _SERVER_RUNNING

    @server_running.setter
    def server_running(self, value: bool):
        global _SERVER_RUNNING
        _SERVER_RUNNING = value

    @property
    def server_started(self):
        global _SERVER_STARTED
        return _SERVER_STARTED

    @server_started.setter
    def server_started(self, value: bool):
        global _SERVER_STARTED
        _SERVER_STARTED = value

    @property
    def name(self):
        return self.NAME

    async def server_start(self, **_kwargs):
        """Call to start when server start signal fire."""
        self.server_running = True
        self.server_started = True

    async def server_stop(self, **_kwargs):
        """Call to stop when server stop signal fire."""
        _server_running = False
        if self.connect:
            logger.debug('Stop kombu connection.')
            self.connect.close()

    async def check_server(self) -> bool:
        """
        检查 server 的状态，如果 server 没启动，
        则等待 5 秒后再次检查，如果仍没有启动，抛出异常。
        :return:
        """
        if not self.server_started:
            logger.info('Server has not start, delay 5 seconds.')
            await asyncio.sleep(5)
            if not self.server_started:
                raise SpiderkeeperError(
                    'Server not started. You should start server or '
                    'call `Kombu.server_start` first.'
                )
        return self.server_running

    @property
    def connect(self) -> Connection:
        """延迟加载单例连接"""
        if self._connect is None:
            self._connect = Connection(settings.MQ)
        return self._connect

    @property
    def channel(self):
        """创建并返回一个新的 channel"""
        return self.connect.channel()

    async def publish(
            self,
            queue_name: str,
            routing_key: str,
            exchange_name: str,
            body: Any
    ) -> None:
        """
        将消息写入队列。
        :param queue_name:
        :param routing_key:
        :param exchange_name:
        :param body:
        :return:
        """
        queue = Queue(name=queue_name, exchange=Exchange(exchange_name), routing_key=routing_key)

        def _publish():
            with producers[self.connect].acquire(block=True) as producer:
                producer.publish(
                    body=body,
                    retry=True,
                    exchange=queue.exchange,
                    routing_key=queue.routing_key,
                    declare=[queue]
                )

        await run_in_executor(_publish)

    async def consume(
            self,
            queue_name: str,
            routing_key: str,
            exchange_name: str,
            register_callbacks: List[Callable],
            limit: Optional[int] = None,
            timeout: Optional[int] = None,
            safety_interval: Optional[int] = 1,
            should_stop: Optional[asyncio.Future] = None,
    ) -> None:
        """

        example:
            def consuming_and_auto_ack(self, items: list[_T], body: _T, message: Message):
                # Consume and auto ack
                items.append(body)
                message.ack()

            data = []   # consumed data
            consume_on_response = functools.partial(consuming_and_auto_ack, data)
            await self.consume(
                queue_name=self.queue_name(app_id),
                routing_key=self.routing_key(app_id),
                register_callbacks=[consume_on_response],
                limit=3,
            )
            for i in data:
                logging.info(i)

        example:
            async def have_to_do_something(item: Any):
                # Have to do something with coroutine
                # when consume each item.
                await asyncio.sleep(0.1)
                logging.info('Consumed data. Detail: %s', item)

            def consuming_and_auto_ack(
                self,
                func: Callable,
                body: _T,
                message: Message,
                loop: Optional[AbstractEventLoop] = None,
            ):
                # Consume and auto ack
                if inspect.iscoroutinefunction(func):
                    # To submit a coroutine object to the event loop. (thread safe)
                    if not loop:
                        raise Exception('You must pass a event loop when call coroutine object.')
                    future = asyncio.run_coroutine_threadsafe(func(body), loop)
                    try:
                        future.result()    # Wait for the result from other os thread
                    except asyncio.TimeoutError:
                        future.cancel()
                        raise
                else:
                    func(body)
                message.ack()

            consume_on_response = functools.partial(consuming_and_auto_ack, have_to_do_something)
            await self.consume(
                queue_name=self.queue_name(app_id),
                routing_key=self.routing_key(app_id),
                register_callbacks=[consume_on_response],
                limit=3,
            )

        example:
            def consuming_and_manual_ack(self, items: list[tuple[_T, Message]], body: _T, message: Message):
                # Consume and auto ack
                items.append((body, message))

            data = []   # consumed data
            consume_on_response = functools.partial(consuming_and_manual_ack, data)
            await self.consume(
                queue_name=self.queue_name(app_id),
                routing_key=self.routing_key(app_id),
                register_callbacks=[consume_on_response],
                limit=3,
            )
            for _body, _message in data:
                logging.info(_body)
                await run_in_executor(_message.ack) # ack

        :param queue_name:
        :param routing_key:
        :param exchange_name:
        :param register_callbacks:  callback 接受两个参数 body 和 message
            注意，不能是 async 函数
            def cb(body: Dict, message: Message):
                logging.debug(body)
                message.ack()
        :param limit:
        :param timeout:
        :param safety_interval:
        :param should_stop:

        :return:
        """
        await self.check_server()
        queue = Queue(name=queue_name, exchange=Exchange(exchange_name), routing_key=routing_key)
        consumer = Consumer(self.channel, queues=[queue])

        for callback in register_callbacks:
            consumer.register_callback(callback)
        consumer.consume()
        await self._consuming(
            limit=limit,
            timeout=timeout,
            safety_interval=safety_interval,
            should_stop=should_stop
        )

    async def _consuming(
            self,
            limit: Optional[int] = None,
            timeout: Optional[int] = None,
            safety_interval: Optional[int] = 1,
            should_stop: Optional[asyncio.Future] = None
    ):
        """

        :param limit:
        :param timeout:
            超时停止消费
        :param safety_interval:
        :param should_stop:
        :return:
        """
        elapsed = 0
        for _ in limit and range(limit) or count():
            server_running = await self.check_server()

            _should_stop = not server_running or (should_stop and should_stop.done())
            # 如果 Server 不在运行，或者 should_stop
            if _should_stop:
                logger.debug('%s should stop, so stop consuming message.', self)
                break

            try:
                await run_in_executor(self.connect.drain_events, timeout=1)
            except socket.timeout:
                self.connect.heartbeat_check()
                # 超时计时，如果超时时间 elapsed 大于给定的超时时间 timeout 则退出
                elapsed += safety_interval
                if timeout and elapsed >= timeout:
                    raise
            except OSError:
                if not _should_stop:
                    raise
            else:
                elapsed = 0


kombu = Kombu()
server_start.connect(kombu.server_start)
server_stop.connect(kombu.server_stop)
