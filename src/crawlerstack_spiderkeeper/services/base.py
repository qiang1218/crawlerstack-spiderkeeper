"""
Base service.
"""

import asyncio
import functools
import inspect
import logging
import socket
from asyncio import AbstractEventLoop
from itertools import count
from typing import Any, Callable, Dict, Generic, List, Optional, Type, Union, TypeVar

from kombu import Connection, Consumer, Exchange, Producer, Queue, Message
from sqlalchemy.ext.asyncio import AsyncSession

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.dao import ProjectDAO
from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db import session_provider
from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.schemas.project import (ProjectCreate,
                                                       ProjectUpdate)
from crawlerstack_spiderkeeper.utils import AppData, AppId, run_in_executor, SingletonMeta
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper.utils.types import (CreateSchemaType, ModelType,
                                                   UpdateSchemaType)

_T = TypeVar('_T')
logger = logging.getLogger(__name__)


class ICRUD:  # noqa
    """
    定义接口规范。
    Service 类都需要实现该接口的抽象方法。

    根据里式替换原则：
        - 当子类的方法实现父类的方法时（重写/重载或实现抽象方法），方法的后置条件（即方法的的输出/返回值）要比父类的方法更严格或相等
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    def get(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def create(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def update(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def delete(self, *args, **kwargs) -> Any:
        raise NotImplementedError


class EntityService(ICRUD, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service."""
    DAO_CLASS: Type[BaseDAO]

    @property
    def dao(self):
        """DAO"""
        return self.DAO_CLASS(self.session)

    @property
    def session(self) -> AsyncSession:
        """Async session"""
        return self._session

    async def get_by_id(self, pk: int) -> ModelType:
        """Get record by primary key."""
        return await self.dao.get_by_id(pk)

    async def get(
            self,
            *,
            sorting_fields: Optional[Union[set[str], list[str]]] = None,
            search_fields: Optional[dict[str, str]] = None,
            limit: int = 5,
            offset: int = 0,
    ) -> list[ModelType]:
        """
        Get multi record.
        :param sorting_fields:
        :param search_fields:
        :param limit:
        :param offset:
        :return:
        """
        return await self.dao.get(
            sorting_fields=sorting_fields,
            search_fields=search_fields,
            limit=limit,
            offset=offset,
        )

    async def create(
            self,
            *,
            obj_in: CreateSchemaType
    ) -> ModelType:
        """
        Create a record.
        :param obj_in:
        :return:
        """
        return await self.dao.create(obj_in=obj_in)

    async def update_by_id(
            self,
            pk: int,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        :param pk:
        :param obj_in:
        :return:
        """
        return await self.dao.update_by_id(pk=pk, obj_in=obj_in)

    async def update(
            self,
            pk: int,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ):
        return await self.update_by_id(pk=pk, obj_in=obj_in)

    async def delete_by_id(self, *, pk: int) -> ModelType:
        """
        Delete a record by primary key.
        :param pk:
        :return:
        """
        return await self.dao.delete_by_id(pk)

    async def delete(self, *, pk: int) -> ModelType:
        """
        Delete a record
        :param pk:
        :return:
        """
        return await self.delete_by_id(pk=pk)

    async def count(self) -> int:
        """
        Count.
        :return:
        """
        return await self.dao.count()


class ProjectService(EntityService[Project, ProjectCreate, ProjectUpdate]):
    """
    Project service.
    """
    DAO_CLASS = ProjectDAO


class SingletonKombu(metaclass=SingletonMeta):
    """
    单例 kombu
    """


# TODO 完善发送确认机制
class Kombu(SingletonKombu, ICRUD):
    """
    Kombu server ，提供队列服务。
    """
    NAME: str

    _connect = None
    _channel = None
    _should_stop = False
    _exchange = None

    @classmethod
    @session_provider(auto_commit=True)
    async def server_start_event(cls, session: AsyncSession):
        obj = cls(session)
        await obj.server_start()

    @classmethod
    @session_provider(auto_commit=True)
    async def server_stop_event(cls, session: AsyncSession):
        obj = cls(session)
        await obj.server_stop()

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

    def queue_name(self, app_id: Optional[AppId] = None):
        """
        Queue name.
        :param app_id:
        :return:
        """
        if app_id:
            return f'{self.name}-{app_id.job_id}'
        return self.name

    def routing_key(self, app_id: Optional[AppId] = None):
        """
        Routing key
        :param app_id:
        :return:
        """
        if app_id:
            return f'{self.name}-{app_id.job_id}'
        return self.name

    def update(self, *args, **kwargs):
        """No operation"""
        pass

    def delete(self, *args, **kwargs):
        """No operation"""
        pass

    async def create(self, app_data: AppData):
        """Create server"""
        await run_in_executor(
            self.publish,
            queue_name=self.queue_name(app_data.app_id),
            routing_key=self.routing_key(app_data.app_id),
            body={'app_id': str(app_data.app_id), 'data': app_data.data}
        )

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

    async def get(self, app_id=None, limit=1):
        """
        Get message data from queue, and auto ack.
        :param app_id:
        :param limit:
        :return:
        """
        data = []
        consume_on_response = functools.partial(self._consuming_and_ack, data)
        await self.consume(
            self.queue_name(app_id),
            self.routing_key(app_id),
            [consume_on_response],
            limit=limit,
        )
        return data

    def _consuming_and_ack(self, items: List[_T], body: _T, message: Message):  # noqa
        """
        用于注册到消费者的回调。 `buffered_data` 用于接收消费的字段，后面两个参数
        是回调的时候传入消息内容。
        在注册回调前，请使用高阶函数 `functools.partial` 将提前定义好的变量封装到该方法中。
        等到执行完成，提前定义的 buffered_data 就有数据了。
        :param items:
        :param body:
        :param message:
        :return:
        """
        items.append(body)
        message.ack()

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
