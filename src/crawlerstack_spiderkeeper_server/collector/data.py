"""storage"""
import asyncio
import logging

from fastapi_sa.database import session_ctx

from crawlerstack_spiderkeeper_server.collector.base import StorageBaseTask
from crawlerstack_spiderkeeper_server.config import settings
from crawlerstack_spiderkeeper_server.schemas.task import TaskUpdate
from crawlerstack_spiderkeeper_server.services import DataService, TaskService
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist
from crawlerstack_spiderkeeper_server.utils.status import Status

# 存储任务的管理需要特殊处理，针对每一个任务开启一个消费者
logger = logging.getLogger(__name__)


class DataBackgroundTask(StorageBaseTask):
    """Data background task"""
    NAME = 'spiderkeeper-data'
    _server_running: bool = None
    data_task_interval = settings.DATA_TASK_INTERVAL
    life_cycle_task: asyncio.Task | None = None

    @property
    def task_service(self):
        """Task service"""
        return TaskService()

    @staticmethod
    async def callback(body: dict):
        """
        消费数据，并将数据写入数据目标库中。
        :param body:
        :return:
        """
        task_name = body.get('task_name')
        data = body.get('data')
        await DataService().create(task_name=task_name, data=data)

    @property
    def server_running(self) -> bool:
        """Server running"""
        return self._server_running

    async def server_start(self, **_):
        """Server start"""
        if self._server_running is None:
            logger.debug('Change %s.server_running to "True"', self.__class__.NAME)
            self._server_running = True

    async def server_stop(self, **_):
        """server stop"""
        logger.debug('Change %s.server_running to "False"', self.__class__.NAME)
        self._server_running = False
        if self.life_cycle_task and not self.life_cycle_task.done():
            self.life_cycle_task.cancel('server stop!')

    @session_ctx
    async def get_tasks(self, **kwargs):
        """get tasks"""
        return await self.task_service.get(**kwargs)

    @session_ctx
    async def update_task(self, **kwargs):
        """Update tasks"""
        return await self.task_service.update(**kwargs)

    async def init_lift_cycle(self, **_):
        """
        Init tasks list cycle
        初始化后台消费者任务状态恢复，调用一次
        :param _:
        :return:
        """
        logger.info('Start the initialization consumption state task')
        _init_task = asyncio.create_task(self._init_lift_cycle())

    async def _init_lift_cycle(self):
        # 仅用来做任务的初始化使用，对历史状态异常修正操作，调用一次
        await asyncio.sleep(5)
        try:
            tasks = await self.get_tasks(search_fields={'consume_status': Status.RUNNING.value})
        except ObjectDoesNotExist:
            logger.debug('Init tasks cycle is empty')
        else:
            for task in tasks:
                # 判断队列，如果没有内容，则进行状态更新
                count = await self.queue_count(task.name, passive=True)
                if count in (0, -1):
                    await self.update_task(pk=task.id,
                                           obj_in=TaskUpdate(consume_status=Status.FINISH.value))  # noqa
                else:
                    await self.update_task(pk=task.id,
                                           obj_in=TaskUpdate(consume_status=Status.STOPPED.value))  # noqa

    async def update_life_cycle(self, **_):
        """
        Update list cycle
        更新后台消费者任务的生命周期
        :param _:
        :return:
        """
        logger.info('Update the consume task list cycle is running')
        self.life_cycle_task = asyncio.create_task(self._update_life_cycle())

    async def _update_life_cycle(self):
        # 异步等待初始化任务完成
        await asyncio.sleep(25)
        _should_clear_tasks = []
        while True:
            logger.debug('Server status %s', self.server_running)
            if not self.server_running:
                break
            # 预留任务等待时间,确认消息最终完成消费
            for task in _should_clear_tasks:
                await self.terminate(task_name=task.get('name'))
                await self.update_task(pk=task.get('id'),
                                       obj_in=TaskUpdate(consume_status=Status.FINISH.value))  # noqa
                await asyncio.sleep(0.5)

            # 获取后台包含的消费者任务
            try:
                _should_clear_tasks = []
                tasks = await self.get_tasks(search_fields={'task_status': Status.EXITED.value,
                                                            'consume_status': Status.RUNNING.value})
            except ObjectDoesNotExist:
                logger.debug('There is no need to quit the data consume task')
            else:
                for task in tasks:
                    try:
                        count = await self.queue_count(task.name, passive=True)
                    except Exception as ex:
                        logger.error(ex)
                    else:
                        if count == 0:
                            _should_clear_tasks.append({'name': task.name, 'id': task.id})
            await asyncio.sleep(self.data_task_interval)
