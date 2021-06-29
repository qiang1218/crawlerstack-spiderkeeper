"""
Base service.
"""
import asyncio
import logging
import socket
from itertools import count
from typing import Any, Callable, Dict, Generic, List, Optional, Union

from kombu import Connection, Consumer, Exchange, Producer, Queue

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.dao import project_dao
from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.schemas.project import (ProjectCreate,
                                                       ProjectUpdate)
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils import AppData, AppId, run_in_executor
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper.utils.types import (CreateSchemaType, ModelType,
                                                   UpdateSchemaType)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service."""
    dao: BaseDAO

    async def get(self, pk: Any) -> ModelType:
        """Get record by primary key."""
        return await run_in_executor(self.dao.get, pk)

    async def get_multi(
            self, *, skip: int = 0, limit: int = 100, order: str = 'DESC', sort: str = 'id'
    ) -> List[ModelType]:
        """
        Get multi record.
        :param skip:
        :param limit:
        :param order:   ASC | DESC
        :param sort:
        :return:
        """
        return await run_in_executor(
            self.dao.get_multi,
            skip=skip,
            limit=limit,
            order=order,
            sort=sort,
        )

    async def create(
            self,
            obj_in: CreateSchemaType
    ) -> ModelType:
        """
        Create a record.
        :param obj_in:
        :return:
        """
        return await run_in_executor(self.dao.create, obj_in=obj_in)

    async def update(
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
        return await run_in_executor(self.dao.update_by_id, pk=pk, obj_in=obj_in)

    async def delete(self, *, pk: int) -> ModelType:
        """
        Delete a record by primary key.
        :param pk:
        :return:
        """
        return await run_in_executor(self.dao.delete_by_id, pk=pk)

    async def count(self) -> int:
        """
        Count.
        :return:
        """
        return await run_in_executor(self.dao.count)


class ProjectService(BaseService[Project, ProjectCreate, ProjectUpdate]):
    """
    Project service.
    """
    dao = project_dao


class KombuMixin:
    """
    Kubo service mixin.
    """
    name: str = ''

    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        if not self.name:
            raise SpiderkeeperError('You should define name')
        try:
            # TODO fix 不要在初始化对象时，初始化连接。
            self.connect = Connection(settings.MQ, confirm_publish=True)
            self.logger.debug('Init kombu connect. url: %s', settings.MQ)
            self.exchange = Exchange(self.name)
            self.logger.debug('Init kombu exchange: %s', self.exchange.name)

            self.channel = self.connect.channel()
        except Exception as ex:
            self.logger.exception('Init kombu error. MQ url: %s, %s', settings.MQ, ex)
            raise

        self.__server_running = False

        # 注册事件
        server_start.connect(self.server_start)
        server_stop.connect(self.server_stop)

    async def server_start(self):
        """Update server to running."""
        self.__server_running = True

    @property
    def server_running(self) -> bool:
        """Server is running?"""
        return self.__server_running

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

    def publish(self, queue_name: str, routing_key: str, body: Any):
        """
        Publish to mq
        :param queue_name:
        :param routing_key:
        :param body:
        :return:
        """
        queue = Queue(name=queue_name, exchange=self.exchange, routing_key=routing_key)
        producer = Producer(self.channel)
        res = producer.publish(
            body=body,
            retry=True,
            exchange=queue.exchange,
            routing_key=queue.routing_key,
            declare=[queue]
        )
        self.logger.debug(
            'Publish data to exchange: %s, queue: %s, routing_key: %s, data: %s',
            queue.exchange.name,
            queue.name,
            routing_key,
            body,
        )
        return res

    def __publish_on_return(self, exception, exchange, routing_key, message):  # pylint: disable=no-self-use
        # TODO 完善发送确认机制
        raise exception

    async def create(self, app_data: AppData):
        """Create server"""
        await run_in_executor(
            self.publish,
            queue_name=self.queue_name(app_data.app_id),
            routing_key=self.routing_key(app_data.app_id),
            body={'app_id': str(app_data.app_id), 'data': app_data.data}
        )

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
        consumer = Consumer(self.connect, queues=[queue])

        for callback in register_callbacks:
            consumer.register_callback(callback)
        consumer.consume()
        self.logger.debug('Consuming from queue: %s', queue_name)
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

            __should_stop = not self.__server_running or (should_stop and should_stop.done())
            if __should_stop:
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
        self.logger.info('Stop consuming.')

    async def server_stop(self):
        """Stop server"""
        self.logger.info('Stop kombu service')
        self.__server_running = False
