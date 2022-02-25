"""
Storage service.
"""
import asyncio
import functools
import logging
from asyncio import AbstractEventLoop
from typing import Callable, Dict

from kombu import Message
from sqlalchemy.ext.asyncio import AsyncSession

from crawlerstack_spiderkeeper.dao import ServerDAO, StorageDAO, TaskDAO
from crawlerstack_spiderkeeper.db import session_provider
from crawlerstack_spiderkeeper.exportors import BaseExporter, exporters_factory
from crawlerstack_spiderkeeper.schemas.storage import (StorageCreate,
                                                       StorageUpdate)
from crawlerstack_spiderkeeper.services.base import EntityService
from crawlerstack_spiderkeeper.services.utils import Kombu
from crawlerstack_spiderkeeper.utils import AppData, AppId
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper.utils.status import Status

logger = logging.getLogger(__name__)


class StorageBackgroundTask:
    """
    存储服务任务。
    根据 APP_ID 将该 job 的数据写入对应的存储位置。
    """
    NAME = 'storage'
    kombu = Kombu()

    @classmethod
    @session_provider()
    async def run_from_cls(
            cls,
            app_id: AppId,
            should_stop: asyncio.Future,
            session: AsyncSession,
    ):
        """
        运行任务
        :param app_id:
        :param should_stop: 传递一个 Future 对象，用来在外部管理该任务的结束
        :param session: session_provider 装饰器会自动注入一个本地化的 session 对象，但不提供自动提交
        :return:
        """
        logger.info(f'Start storage task, app id: "{app_id}"')
        obj = cls(app_id, session, should_stop)
        await obj.start()

    def __init__(self, app_id: AppId, session: AsyncSession, should_stop: asyncio.Future):
        self._app_id = app_id
        self._should_stop = should_stop
        self._session = session
        self._task_dao = TaskDAO(self.session)
        self._server_dao = ServerDAO(self.session)
        self._storage_dao = StorageDAO(self.session)

    @property
    def session(self) -> AsyncSession:
        return self._session

    @property
    def app_id(self):
        return self._app_id

    @property
    def should_stop(self) -> asyncio.Future:
        return self._should_stop

    @property
    def server_dao(self) -> ServerDAO:
        return self._server_dao

    @property
    def storage_dao(self) -> StorageDAO:
        return self._storage_dao

    @property
    def background_task_id(self) -> str:
        return f'{self.NAME}-{self.app_id.job_id}'

    @property
    def queue_name(self) -> str:
        return self.background_task_id

    @property
    def routing_key(self) -> str:
        return self.background_task_id

    @property
    def exchange_name(self) -> str:
        return self.NAME

    async def exporter(self) -> BaseExporter:
        """Get exporter by job id."""
        job_id = self.app_id.job_id
        async with self.session.begin():
            server = await self.server_dao.get_server_by_job_id(job_id)
            if server:
                exporter_cls = exporters_factory(server.type)
                if exporter_cls:
                    return exporter_cls.from_url(server.uri)
                raise SpiderkeeperError(
                    f'Exporter schema: {server.type} is not support. Please implementation',
                )
            raise SpiderkeeperError(f'Job<id: {job_id}> not config server info.')

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

        async def increase_storage_count():
            """封装一个方法，手动开启事务。"""
            async with self.session.begin():
                await self.storage_dao.increase_storage_count(storage_id)

        print('callback event_loop status:', id(loop), loop.is_running())
        # 在一个线程中运行其他线程的异步任务。通过 loop 指定运行在那个线程的事件循环上
        future = asyncio.run_coroutine_threadsafe(
            increase_storage_count(),
            loop
        )
        try:
            future.result()  # 同步阻塞等待该任务完成
        except asyncio.TimeoutError:
            future.cancel()
            raise

        message.ack()  # 手动 ack

    async def consume_task(self):
        """
        消费队列数据，同时更新数据库状态。该方法是阻塞任务，应放在后台运行
        :return:
        """
        logger.debug('Start storage consume task: %s', self.app_id)
        state = Status.RUNNING
        detail = None
        async with self.session.begin():  # 手动开启事务
            storage_obj = await self.storage_dao.get_by_job_id(self.app_id.job_id)
            if not storage_obj:
                storage_obj = await self.storage_dao.create(
                    obj_in=StorageCreate(job_id=self.app_id.job_id, state=state.value)
                )
        storage_id = storage_obj.id
        logger.debug('Consume task for storage id: %d', storage_id)
        event_loop = asyncio.get_running_loop()
        try:
            exporter = await self.exporter()
            callback = functools.partial(
                self._consuming_and_callback,
                callback=exporter.write,
                storage_id=storage_id,
                loop=event_loop,
            )
            logger.debug('Kombu start consuming...')
            # 阻塞，后台消费
            await self.kombu.consume(
                queue_name=self.queue_name,
                routing_key=self.queue_name,
                exchange_name=self.exchange_name,
                should_stop=self.should_stop,
                register_callbacks=[callback],
            )
            logger.debug('Consume task finish.')
            state = Status.FINISH
        except SpiderkeeperError as ex:
            logger.debug('Consume fail.')
            state = Status.FAILURE
            detail = str(ex)
            logger.error(ex)

        logger.debug('storage task : %s %s', self.app_id, state)
        async with self.session.begin():
            await self.storage_dao.update_by_id(
                pk=storage_id,
                obj_in=StorageUpdate(state=state.value, detail=detail),
            )

    async def start(self):
        """
        Start storage
        :return:
        """
        await self.consume_task()

    async def stop(self):
        """Stop storage task"""
        self.should_stop.set_result('Stop')


class StorageService(EntityService):
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

    注意：在服务器停止时，是通过信号设置 Kombu 中的全局变量控制正在运行的任务进行停止的，
    即任务在运行的过程中会检测该变量。
    暂时不确定是否会出现无法停止任务的情况。
    """
    DAO_CLASS = StorageDAO
    NAME = 'storage'
    kombu = Kombu()

    _storage_background_tasks: dict[str, asyncio.Future] = {}

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._task_dao = TaskDAO(self.session)
        self._server_dao = ServerDAO(self.session)
        self._storage_dao = StorageDAO(self.session)

    @property
    def task_dao(self) -> TaskDAO:
        return self._task_dao

    @property
    def storage_dao(self) -> StorageDAO:
        return self._storage_dao

    @property
    def storage_background_tasks(self) -> dict[str, asyncio.Future]:
        return self._storage_background_tasks.copy()

    @property
    def event_loop(self) -> AbstractEventLoop:
        """Current running event loop."""
        return asyncio.get_running_loop()

    def queue_name(self, job_id: int) -> str:
        return self.background_task_id(job_id)

    def routing_key(self, job_id: int) -> str:
        return self.background_task_id(job_id)

    def background_task_id(self, job_id: int) -> str:
        return f'{self.NAME}-{job_id}'

    async def create(self, app_data: AppData):
        """Create storage task."""
        await self.kombu.publish(
            queue_name=self.queue_name(app_data.app_id.job_id),
            routing_key=self.routing_key(app_data.app_id.job_id),
            exchange_name=self.NAME,
            body=app_data.data,
        )
        await self.task_dao.increase_item_count(app_data.app_id.task_id)

        logger.debug('Increase task: %s item count.', app_data.app_id.task_id)

    async def is_running(self, job_id: int) -> bool:
        running_storage = await self.storage_dao.running_storage()
        for storage in running_storage:
            task_id = self.background_task_id(storage.job_id)  # 后台任务 id
            # 如果后台任务列表中没有该任务，但数据库中该任务的状态不是完成或停止，
            # 则更新数据库中的任务状态为停止。
            # 因为这种状态是由于任务没有正常停止造成的。
            # 比如服务器突然宕机
            # 某些为止逻辑问题，导致状态不一致。
            if task_id not in self._storage_background_tasks and storage.state > 0:
                logger.info(
                    'Because storage: %s already stop, update db state',
                    storage.id
                )
                await self.storage_dao.update_by_id(
                    pk=storage.id,
                    obj_in=StorageUpdate(
                        state=Status.STOPPED.value,
                        detail='storage task already stop, update db state'
                    )
                )
        # 检查任务是否在正在运行的任务列表中
        if self.background_task_id(job_id) in self._storage_background_tasks:
            return True
        return False

    async def start(self, app_id: AppId) -> str:
        """启动一个任务"""
        if await self.is_running(app_id.job_id):
            msg = 'Storage task already run.'
        else:
            future = asyncio.Future()
            task = self.event_loop.create_task(
                StorageBackgroundTask.run_from_cls(
                    app_id=app_id,
                    should_stop=future
                )
            )
            task.add_done_callback(
                functools.partial(
                    self._storage_background_tasks.pop,
                    self.background_task_id(app_id.job_id)
                )
            )
            self._storage_background_tasks.setdefault(self.background_task_id(app_id.job_id), future)  # noqa
            msg = 'Run storage task.'

        return msg

    async def stop(self, app_id: AppId) -> str:
        """停止任务"""
        if self.background_task_id(app_id.job_id) in self._storage_background_tasks:
            fut = self._storage_background_tasks.pop(self.background_task_id(app_id.job_id), None)
            if fut and not fut.done():
                fut.set_result(True)
                logger.debug('Stopping storage task: %s', app_id)
                msg = 'Stopping storage task.'
            else:
                msg = 'Task already stopped.'
        else:
            msg = 'No storage task.'
        return msg
