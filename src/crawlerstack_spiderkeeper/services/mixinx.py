import asyncio
import logging
import socket
import contextlib
from functools import partial
from itertools import count
from typing import Type, TypeVar

from kombu import Consumer, Connection, connections, Queue, Exchange, Message, producers, Producer
from kombu.utils.encoding import safe_repr

from crawlerstack_spiderkeeper.utils import run_in_executor

_T = TypeVar('_T')

logger = logging.getLogger(__name__)


class ProducerConsumerMixin:
    connect_max_retries = None
    should_stop = False

    connect: Connection

    _consumer_connection = None
    _producer_connection = None
    NAME: str

    def __init__(self):
        self._data = []

    @property
    def producer_connection(self) -> Connection:
        if self._producer_connection is None:
            conn = self.connect.clone()

            self._producer_connection = conn
        return self._producer_connection

    @property
    def consumer_connection(self) -> Connection:
        if self._consumer_connection is None:
            conn = self.connect.clone()

            self._consumer_connection = conn
        return self._consumer_connection

    @property
    def queue_name(self):
        return self.NAME

    @property
    def routing_key(self):
        return self.NAME

    @property
    def exchange_name(self):
        return self.NAME

    @property
    def queue(self) -> Queue:
        return Queue(
            name=self.queue_name,
            exchange=Exchange(self.exchange_name),
            routing_key=self.routing_key
        )

    @property
    def data(self) -> list[_T]:
        return self._data

    async def consume(self):
        """"""

    def callback_on_consuming(self, body: _T, message: Message):  # noqa
        self._data.append(body)
        print(body)
        message.ack()

    async def on_iteration(self):
        for i in self._data:
            yield i

    def on_connection_error(self, exc, interval):  # noqa
        logger.warning('Broker connection error, trying again in %s seconds: %r.', interval, exc)

    async def on_consume_ready(self, connection, channel, consumers, **kwargs):
        pass

    async def on_connection_revived(self):
        """"""

    def on_consume_end(self, connection, channel):
        """"""

    def on_decode_error(self, message, exc):  # noqa
        logger.error(
            "Can't decode message body: %r (type:%r encoding:%r raw:%r')",
            exc, message.content_type, message.content_encoding,
            safe_repr(message.body)
        )
        message.ack()

    def on_consume_end(self, connection, channel):  # noqa
        if self._producer_connection is not None:
            self._producer_connection.close()
            self._producer_connection = None

    @contextlib.asynccontextmanager
    async def producer(self):
        async with self.establish_connection(self.consumer_connection) as connect:
            await self.on_connection_revived()
            producer: Producer = producers[connect].acquire(block=True)
            await run_in_executor(producer.__enter__)
            yield connect, producer
            await run_in_executor(producer.__exit__)

    async def produce(self, data):
        """"""
        async with self.producer() as (connect, producer):
            await run_in_executor(
                producer.publish,
                body=data,
                exchange=self.queue.exchange,
                routing_key=self.queue.routing_key,
                declare=[self.queue],
            )

    @contextlib.asynccontextmanager
    async def establish_connection(self, connection: Connection):
        connect: Connection = connections[connection].acquire(block=True)
        await run_in_executor(connect.__enter__)
        await run_in_executor(
            connect.ensure_connection,
            self.on_connection_error,
            self.connect_max_retries,
        )
        yield connect
        await run_in_executor(connect.__exit__)

    @contextlib.asynccontextmanager
    async def get_consumers(self, consumer_kls: partial[Consumer], channel):
        consumer = consumer_kls(queues=[self.queue])
        consumer.register_callback(self.callback_on_consuming)
        yield consumer

    @contextlib.asynccontextmanager
    async def consumer(self):
        """通过连接对象初始化 consumer"""
        async with self.establish_connection(self.consumer_connection) as connect:
            await self.on_connection_revived()
            logger.info('Connected to %s', connect.as_uri())
            # TODO
            channel = self.connect.channel()
            await run_in_executor(channel.__enter__)
            cls = partial(
                Consumer,
                channel,
                on_decode_error=self.on_decode_error
            )
            async with self.get_consumers(cls, channel) as consumer:
                yield connect, channel, consumer
            await run_in_executor(channel.__exit__)
            logger.debug('Consumers canceled')
            self.on_consume_end(connect, channel)
        logger.debug('Connection closed')

    @contextlib.asynccontextmanager
    async def extra_context(self, connection, channel):
        """"""
        yield

    @contextlib.asynccontextmanager
    async def consumer_context(self, **kwargs):
        async with self.consumer() as (connection, channel, consumer):
            yield connection, channel, consumer

    async def consuming(self, limit: int, timeout=None, safety_interval=1, **kwargs):
        elapsed = 0
        async with self.consumer_context(**kwargs) as (conn, channel, consumers):
            for _ in limit and range(limit) or count():
                if self.should_stop:
                    break
                try:
                    await run_in_executor(self.connect.drain_events, timeout=safety_interval)
                except socket.timeout:
                    conn.heartbeat_check()
                    elapsed += safety_interval
                    if timeout and elapsed >= timeout:
                        raise
                except OSError:
                    if not self.should_stop:
                        raise
                else:
                    elapsed = 0
        logger.debug('consume exiting')


class Demo(ProducerConsumerMixin):
    connect = Connection()
    NAME = 'metric'
