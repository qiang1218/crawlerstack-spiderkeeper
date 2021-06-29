"""
Storage service.
"""
import asyncio
import functools
from asyncio import AbstractEventLoop
from typing import Callable, Dict, Optional

from kombu import Message

from crawlerstack_spiderkeeper.dao import server_dao, storage_dao, task_dao
from crawlerstack_spiderkeeper.db.models import Server, Storage
from crawlerstack_spiderkeeper.exportors import BaseExporter, exporters_factory
from crawlerstack_spiderkeeper.schemas.storage import (StorageCreate,
                                                       StorageUpdate)
from crawlerstack_spiderkeeper.services.base import KombuMixin
from crawlerstack_spiderkeeper.utils import AppData, AppId, run_in_executor
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper.utils.states import States


class StorageService(KombuMixin):
    """
    Storage service.
    """
    name = 'storage'

    def __init__(self):
        super().__init__()
        self.__storage_tasks: Dict[str, asyncio.Future] = {}

    @property
    def _event_loop(self) -> AbstractEventLoop:
        """Current running event loop."""
        return asyncio.get_running_loop()

    async def create(self, app_data: AppData):
        """Create storage task."""
        await super().create(app_data)

        await run_in_executor(
            task_dao.increase_item_count,
            pk=app_data.app_id.task_id,
        )
        self.logger.debug('Increase task: %s item count.', app_data.app_id.task_id)

    async def _exporter(self, job_id: int) -> BaseExporter:
        """Get exporter by job id."""
        server: Server = await run_in_executor(server_dao.get_server_by_job_id, job_id)
        if server:
            exporter_cls = exporters_factory(server.type)
            if exporter_cls:
                return exporter_cls.from_url(server.uri)
            raise SpiderkeeperError(
                f'Exporter schema: {server.type} is not support. Please implementation',
            )
        raise SpiderkeeperError(f'Job<id: {job_id}> not config server info.')

    def callback(self, func: Callable, storage_id: int, body: Dict, message: Message):
        """
        Consumer 回调，消费数据然后写入到某个地方。
        注意：回调不支持异步方法。
        :param func:
        :param storage_id:
        :param body:
        :param message:
        :return:
        """
        try:
            func(body.get('data'))
        except Exception as ex:  # pylint: disable=broad-except
            self.logger.error('Consume data error. %s', ex)
        # 如果没有异常，则更新状态，同时 ack
        else:
            # 由于 kombu consume 的回调不支持异步，所以这里使用同步操作。
            storage_dao.increase_storage_count(storage_id)
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
        self.logger.debug('Start storage consume task: %s', app_id)
        state = States.RUNNING
        detail = None

        storage_obj: Storage = await run_in_executor(
            storage_dao.create,
            obj_in=StorageCreate(job_id=app_id.job_id, state=state),
        )
        try:
            exporter = await self._exporter(job_id=app_id.job_id)
            callback = functools.partial(self.callback, exporter.write, storage_obj.id)
            # 阻塞，后台消费
            await self.consume(
                queue_name=self.queue_name(app_id),
                routing_key=self.queue_name(app_id),
                should_stop=should_stop,
                register_callbacks=[callback],
            )
            state = States.FINISH
        except Exception as ex:  # pylint: disable=broad-except
            state = States.FAILURE
            detail = str(ex)
            self.logger.error(ex)
        # 消费任务完成，移除任务引用

        # 再次清理 task 的 fut 。如果返回 False 说明 fut 已经在 self.stop 的时候被清理了
        # 如果返回 True 则说明没有通过 self.stop 调用。也就是说 上面阻塞消费逻辑已经自己结束，或者出现异常。
        # 如果 server_stop ，阻塞消费的逻辑会自动结束。
        self._clean_storage_task(app_id)

        self.logger.debug('storage task : %s %s', app_id, state)
        await run_in_executor(
            storage_dao.update_by_id,
            pk=storage_obj.id,
            obj_in=StorageUpdate(state=state, detail=detail),
        )

    async def has_running_task(self, app_id: AppId) -> bool:
        """
        Check has running task.
        :param app_id:
        :return:
        """
        running_storage = await run_in_executor(storage_dao.running_storage)
        if str(app_id) not in self.__storage_tasks:
            # 如果没有 Storage 任务，则更新数据库状态
            if running_storage:
                for storage in running_storage:
                    self.logger.debug(
                        'Because storage: %s already stop, update db state',
                        storage.id
                    )
                    await run_in_executor(
                        storage_dao.update_by_id,
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
            self.__storage_tasks.update({str(app_id): fut})
            self._event_loop.create_task(self.consume_task(app_id, fut))
            return 'Run storage task.'
        return 'Storage task already run.'

    def _clean_storage_task(self, app_id: AppId) -> Optional[bool]:
        """
        如果正常停止 fut 返回 true
        :param app_id:
        :return:
        """
        fut = self.__storage_tasks.pop(str(app_id), None)
        if fut and not fut.done():
            fut.set_result(True)
            return True
        return None

    async def stop(self, app_id: AppId) -> str:
        """Stop storage task"""
        if str(app_id) in self.__storage_tasks:
            self._clean_storage_task(app_id)
            self.logger.debug('Stopping storage task: %s', app_id)
            return 'Stopping storage task.'
        return 'No storage task.'

    @property
    def storage_tasks(self):
        """
        Get all storage tasks.
        :return:
        """
        return self.__storage_tasks

    async def server_stop(self):
        """
        Stop server.
        :return:
        """
        await super().server_stop()
        if not self.server_running:
            self.logger.debug('Server stop, clean storage task.')
            _storage_tasks = self.__storage_tasks.copy()
            for _, fut in _storage_tasks.items():
                if fut and not fut.done():
                    fut.set_result(True)
                    _ = self.__storage_tasks.pop(_, None)
