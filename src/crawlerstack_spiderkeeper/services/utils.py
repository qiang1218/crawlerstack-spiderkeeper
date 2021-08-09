import asyncio
import logging
import socket
from itertools import count
from typing import Any, Callable, List, Optional, TypeVar

from kombu import Connection, Consumer, Exchange, Producer, Queue, connections

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.utils import run_in_executor, SingletonMeta
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError

_T = TypeVar('_T')


# TODO 完善发送确认机制
class Kombu(metaclass=SingletonMeta):
    """
    Kombu server ，提供队列服务。

    具有单例性质。
    """
    NAME: str

    _connect = None
    _channel = None
    _should_stop = False
    _exchange = None

    async def server_start(self):
        """Call to start when server start signal fire."""
        self._should_stop = True

    async def server_stop(self):
        """Call to stop when server stop signal fire."""
        self._should_stop = True

    @property
    def name(self) -> str:
        """Server name"""
        if not self.NAME:
            raise SpiderkeeperError('You should define name')
        return self.NAME

    @property
    def should_stop(self) -> bool:
        return self._should_stop

    @property
    def exchange(self):
        """Delay load exchange"""
        if self._exchange is None:
            self._exchange = Exchange(self.name)
        return self._exchange

    @property
    def connect(self) -> Connection:
        """延迟加载单例连接"""
        if self._connect is None:
            self._connect = Connection(settings.MQ, confirm_publish=True)
        return self._connect

    @property
    def channel(self):
        """延迟加载单例 channel """
        if self._channel is None:
            self._channel = self.connect.channel()
        return self._channel

    def queue_name(self) -> str:
        """Default queue name"""
        return self.name

    def routing_key(self) -> str:
        """Default routing key"""
        return self.name

    async def publish(self, queue_name: str, routing_key: str, body: Any):
        """
        将消息写入队列。
        :param queue_name:
        :param routing_key:
        :param body:
        :return:
        """
        queue = Queue(name=queue_name, exchange=self.exchange, routing_key=routing_key)
        producer = Producer(self.channel)
        result = await run_in_executor(
            producer.publish,
            body=body,
            content_type='json',
            retry=True,
            exchange=queue.exchange,
            routing_key=queue.routing_key,
            declare=[queue]
        )

        return result

    async def consume(
            self,
            queue_name: str,
            routing_key: str,
            register_callbacks: List[Callable],
            limit: Optional[int] = None,
            timeout: Optional[int] = None,
            safety_interval: Optional[int] = 1,
            should_stop: Optional[asyncio.Future] = None,
    ) -> None:
        """
        example:
            def consuming_and_auto_ack(self, items: List[_T], body: _T, message: Message):
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
            def consuming_and_manual_ack(self, items: List[Tuple[_T, Message]], body: _T, message: Message):
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
        queue = Queue(name=queue_name, exchange=self.exchange, routing_key=routing_key)
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
            __should_stop = self._should_stop or (should_stop and should_stop.done())
            if __should_stop:
                logging.debug('%s should stop, so stop consuming message.', self)
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
                if not __should_stop:
                    raise
            else:
                elapsed = 0
