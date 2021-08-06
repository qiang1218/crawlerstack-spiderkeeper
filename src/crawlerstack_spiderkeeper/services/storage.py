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
from crawlerstack_spiderkeeper.services.base import EntityService, Kombu
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils import AppData, AppId
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper.utils.states import States

logger = logging.getLogger(__name__)


class StorageService(Kombu, EntityService):
    """
    存储服务。
    接口接收任务写进来的数据，并将数据存入缓存队列。
    启动后台任务后，会将数据导出到存储位置
    """
    NAME = 'storage'

    DAO_CLASS = StorageDAO

    _storage_tasks: Dict[str, asyncio.Future] = {}

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

    async def create(self, app_data: AppData):
        """Create storage task."""
        await super().create(app_data)
        await self.task_dao.increase_item_count(app_data.app_id.task_id)
        logger.debug('Increase task: %s item count.', app_data.app_id.task_id)

    async def get_server_by_job_id(self, job_id: int):
        return self.server_dao.get_server_by_job_id(job_id)

    async def exporter(self, job_id: int):
        """Get exporter by job id."""
        server = await self.server_dao.get_server_by_job_id(job_id)
        return server
        # if server:
        #     exporter_cls = exporters_factory(server.type)
        #     if exporter_cls:
        #         return exporter_cls.from_url(server.uri)
        #     raise SpiderkeeperError(
        #         f'Exporter schema: {server.type} is not support. Please implementation',
        #     )
        # raise SpiderkeeperError(f'Job<id: {job_id}> not config server info.')

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

        storage_obj = await self.storage_dao.create(obj_in=StorageCreate(job_id=app_id.job_id, state=state))

        try:
            exporter = await self.exporter(job_id=app_id.job_id)
            callback = functools.partial(
                self._consuming_and_callback,
                callback=exporter.write,
                storage_id=storage_obj.id,
                loop=asyncio.get_running_loop,
            )
            # 阻塞，后台消费
            await self.consume(
                queue_name=self.queue_name(app_id),
                routing_key=self.queue_name(app_id),
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
            obj_in=StorageUpdate(state=state, detail=detail),
        )

    async def has_running_task(self, app_id: AppId) -> bool:
        """
        Check has running task.
        :param app_id:
        :return:
        """
        running_storage = await self.storage_dao.running_storage()
        if str(app_id) not in self._storage_tasks:
            # 如果没有 Storage 任务，则更新数据库状态
            if running_storage:
                for storage in running_storage:
                    logger.debug(
                        'Because storage: %s already stop, update db state',
                        storage.id
                    )
                    await self.storage_dao.update_by_id(
                        pk=storage.id,
                        obj_in=StorageUpdate(
                            state=States.STOPPED,
                            detail='storage task already stop, update db state'
                        )
                    )

            return True

    async def start(self, app_id: AppId) -> str:
        """
        Start storage
        :param app_id:
        :return:
        """
        fut = asyncio.Future()
        if await self.has_running_task(app_id):
            self._storage_tasks.update({str(app_id): fut})
            self.event_loop.create_task(self.consume_task(app_id, fut))
            return 'Run storage task.'
        return 'Storage task already run.'

    def _clean_storage_task(self, app_id: AppId) -> Optional[bool]:
        """
        如果正常停止 fut 返回 true
        :param app_id:
        :return:
        """
        fut = self._storage_tasks.pop(str(app_id), None)
        if fut and not fut.done():
            fut.set_result(True)
            return True
        return None

    async def stop(self, app_id: AppId) -> str:
        """Stop storage task"""
        if str(app_id) in self._storage_tasks:
            self._clean_storage_task(app_id)
            logger.debug('Stopping storage task: %s', app_id)
            return 'Stopping storage task.'
        return 'No storage task.'

    async def server_stop(self):
        """
        Stop server.
        :return:
        """
        await super().server_stop()
        if not self._should_stop:
            logger.debug('Server stop, clean storage task.')
            _storage_tasks = self._storage_tasks.copy()
            for _, fut in _storage_tasks.items():
                if fut and not fut.done():
                    fut.set_result(True)
                    _ = self._storage_tasks.pop(_, None)


# 注册事件
# server_start.connect(StorageService.server_start)
# server_stop.connect(StorageService.server_stop)
