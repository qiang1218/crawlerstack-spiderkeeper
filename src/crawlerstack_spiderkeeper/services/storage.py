"""
Storage service.
"""
import asyncio
import functools
import logging
from asyncio import AbstractEventLoop
from typing import Callable, Dict, Optional

from kombu import Message
from sqlalchemy.ext.asyncio import AsyncSession

from crawlerstack_spiderkeeper.dao import ServerDAO, StorageDAO, TaskDAO
from crawlerstack_spiderkeeper.exportors import BaseExporter, exporters_factory
from crawlerstack_spiderkeeper.schemas.storage import (StorageCreate,
                                                       StorageUpdate)
from crawlerstack_spiderkeeper.services.base import EntityService, ServerEventMixin
from crawlerstack_spiderkeeper.services.utils import Kombu
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils import AppData, AppId
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper.utils.states import States

logger = logging.getLogger(__name__)


class StorageKombu(Kombu):
    NAME = 'storage'


class StorageService(EntityService, ServerEventMixin):
    """
    存储服务。
    接口接收任务写进来的数据，并将数据存入缓存队列。
    启动后台任务后，会将数据导出到存储位置

    存储服务为一个 Job 提供一个后台任务，和一个队列服务。
    当数据写入时，会现构造一个 queue_name 和 routing_key
    格式为 `<NAME>-<job_id>` 。

    当启动存储导出任务时，会在后台创建一个导出任务，通过 job 设置的
    服务器类型初始化导出对象，然后将创建的任务保存在 _storage_tasks 中，
    key 值格式为 `<NAME>-<job_id>`

    在服务器停止时，会将所有后台任务停止。
    """
    DAO_CLASS = StorageDAO

    _storage_tasks: Dict[str, asyncio.Future] = {}

    kombu = StorageKombu()

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._task_dao = TaskDAO(self.session)
        self._server_dao = ServerDAO(self.session)
        self._storage_dao = StorageDAO(self.session)

    @property
    def storage_tasks(self):
        """
        Get all storage tasks.
        :return:
        """
        return self._storage_tasks

    @property
    def server_dao(self) -> ServerDAO:
        return self._server_dao

    @property
    def task_dao(self) -> TaskDAO:
        return self._task_dao

    @property
    def storage_dao(self) -> StorageDAO:
        return self._storage_dao

    @property
    def event_loop(self) -> AbstractEventLoop:
        """Current running event loop."""
        return asyncio.get_running_loop()

    def queue_name(self, job_id: int) -> str:
        return self.storage_task_id(job_id)

    def routing_key(self, job_id: int) -> str:
        return self.storage_task_id(job_id)

    def storage_task_id(self, job_id: int) -> str:
        return f'{self.kombu.name}-{job_id}'

    async def create(self, app_data: AppData):
        """Create storage task."""
        await self.kombu.publish(
            queue_name=self.queue_name(app_data.app_id.job_id),
            routing_key=self.routing_key(app_data.app_id.job_id),
            body=app_data.data,
        )
        await self.task_dao.increase_item_count(app_data.app_id.task_id)
        logger.debug('Increase task: %s item count.', app_data.app_id.task_id)

    async def exporter(self, job_id: int):
        """Get exporter by job id."""
        server = await self.server_dao.get_server_by_job_id(job_id)
        if server:
            exporter_cls = exporters_factory(server.type)
            if exporter_cls:
                return exporter_cls.from_url(server.uri)
            raise SpiderkeeperError(
                f'Exporter schema: {server.type} is not support. Please implementation',
            )
        raise SpiderkeeperError(f'Job<id: {job_id}> not config server info.')

    async def exporting(self, exporter: BaseExporter, data, storage_id):
        exporter.write(data)
        await self.storage_dao.increase_storage_count(storage_id)

    def _consuming_and_callback(  # noqa
            self,
            body: Dict,
            message: Message,
            *,
            callback: Callable,
            storage_id: int,
            loop: AbstractEventLoop,
    ) -> None:
        """
        注册到 kombu 中的回调，会一直消费队列中的数据。
        同时在每次消费完成后，执行数据库更新，更新完成会进行消费确认。
        :param body: 队列中的数据
        :param message:
        :param storage_id:
        :param loop:
        :return:
        """
        callback(body)
        future = asyncio.run_coroutine_threadsafe(
            self.storage_dao.increase_storage_count(storage_id),
            loop
        )
        try:
            future.result()  # Wait for the result from other os thread
        except asyncio.TimeoutError:
            future.cancel()
            raise

        message.ack()

    async def consume_task(
            self,
            app_id: AppId,
            should_stop: asyncio.Future,
    ):
        """
        消费队列数据，同时更新数据库状态。该方法是阻塞任务，应放在后台运行
        :param app_id:
        :param should_stop:
        :return:
        """
        logger.debug('Start storage consume task: %s', app_id)
        state = States.RUNNING
        detail = None

        storage_obj = await self.storage_dao.create(
            obj_in=StorageCreate(job_id=app_id.job_id, state=state.value)
        )

        try:
            exporter = await self.exporter(job_id=app_id.job_id)
            callback = functools.partial(
                self._consuming_and_callback,
                callback=exporter.write,
                storage_id=storage_obj.id,
                loop=asyncio.get_running_loop,
            )
            # 阻塞，后台消费
            await self.kombu.consume(
                queue_name=self.queue_name(app_id.job_id),
                routing_key=self.queue_name(app_id.job_id),
                should_stop=should_stop,
                register_callbacks=[callback],
            )
            state = States.FINISH
        except SpiderkeeperError as ex:
            state = States.FAILURE
            detail = str(ex)
            logger.error(ex)
        # 消费任务完成，移除任务引用

        # 再次清理 task 的 fut 。如果返回 False 说明 fut 已经在 self.stop 的时候被清理了
        # 如果返回 True 则说明没有通过 self.stop 调用。也就是说 上面阻塞消费逻辑已经自己结束，或者出现异常。
        # 如果 server_stop ，阻塞消费的逻辑会自动结束。
        self._clean_storage_task(app_id)

        logger.debug('storage task : %s %s', app_id, state)
        await self.storage_dao.update_by_id(
            pk=storage_obj.id,
            obj_in=StorageUpdate(state=state.value, detail=detail),
        )

    async def has_running_task(self, job_id: int) -> bool:
        """
        检查是否有正在运行的 task
        每次调用时，现检查现有任务的情况。
        :param job_id:
        :return:
        """
        running_storage = await self.storage_dao.running_storage()
        # 如果检查的 app_id 不在任务列表中
        if self.storage_task_id(job_id) in self._storage_tasks:
            return True
        else:
            for storage in running_storage:

                task_id = self.storage_task_id(storage.job_id)  # 后台任务 id
                # 如果没有后台任务，并且状态 > 0 ，将其更新失败
                # 因为这种状态是由于任务没有正常停止造成的。
                # 比如服务器突然宕机
                # 某些为止逻辑问题，导致状态不一致。
                if task_id not in self._storage_tasks and storage.state > 0:
                    logger.info(
                        'Because storage: %s already stop, update db state',
                        storage.id
                    )
                    await self.storage_dao.update_by_id(
                        pk=storage.id,
                        obj_in=StorageUpdate(
                            state=States.STOPPED.value,
                            detail='storage task already stop, update db state'
                        )
                    )

    async def start(self, app_id: AppId) -> str:
        """
        Start storage
        :param app_id:
        :return:
        """
        fut = asyncio.Future()
        # 如果任务没有运行，就创建。
        if not await self.has_running_task(app_id.job_id):
            # 使用 `<NAME>-<job_id>` 构造后台任务的 key
            self._storage_tasks.update({self.storage_task_id(app_id.job_id): fut})
            self.event_loop.create_task(self.consume_task(app_id, fut))
            return 'Run storage task.'
        return 'Storage task already run.'

    def _clean_storage_task(self, job_id: int) -> Optional[bool]:
        """
        如果正常停止 fut 返回 true
        :param job_id:
        :return:
        """
        fut = self._storage_tasks.pop(self.storage_task_id(job_id), None)
        if fut and not fut.done():
            fut.set_result(True)
            return True
        return None

    async def stop(self, app_id: AppId) -> str:
        """Stop storage task"""
        if self.storage_task_id(app_id.job_id) in self._storage_tasks:
            self._clean_storage_task(app_id.job_id)
            logger.debug('Stopping storage task: %s', app_id)
            return 'Stopping storage task.'
        return 'No storage task.'

    async def server_stop(self):
        """
        Stop server.
        :return:
        """
        await self.kombu.server_stop()
        if self.kombu.should_stop:
            logger.debug('Server stop, clean storage task.')
            _storage_tasks = self._storage_tasks.copy()
            for _, fut in _storage_tasks.items():
                if fut and not fut.done():
                    fut.set_result(True)
                    _ = self._storage_tasks.pop(_, None)


# 注册事件
server_start.connect(StorageService.server_start_event)
server_stop.connect(StorageService.server_stop_event)
