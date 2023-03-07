"""Task life cycle"""
import asyncio
import logging
from datetime import datetime

from fastapi_sa.database import session_ctx

from crawlerstack_spiderkeeper_scheduler.config import settings
from crawlerstack_spiderkeeper_scheduler.schemas.container import \
    ContainerSchema
from crawlerstack_spiderkeeper_scheduler.schemas.executor import ExecutorSchema
from crawlerstack_spiderkeeper_scheduler.schemas.task import TaskSchema
from crawlerstack_spiderkeeper_scheduler.services.executor import \
    ExecutorService
from crawlerstack_spiderkeeper_scheduler.services.task import TaskService
from crawlerstack_spiderkeeper_scheduler.utils import SingletonMeta
from crawlerstack_spiderkeeper_scheduler.utils.request import RequestWithHttpx
from crawlerstack_spiderkeeper_scheduler.utils.status import Status

logger = logging.getLogger(__name__)


class LifeCycle(metaclass=SingletonMeta):
    """Life cycle"""

    name = 'task_life_cycle'
    life_cycle: asyncio.Task | None = None
    _server_running = None

    def __init__(self):
        self.settings = settings
        self.job_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_JOB_SUFFIX
        self.artifact_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_ARTIFACT_SUFFIX
        self.server_task_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_TASK_SUFFIX
        self.server_task_crud_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_TASK_CRUD_SUFFIX
        # 使用过程基于执行器的url进行拼接
        self.executor_run_url_suffix = self.settings.EXECUTOR_RUN_SUFFIX
        self.executor_wait_url_suffix = self.settings.EXECUTOR_WAIT_SUFFIX
        self.executor_rm_url_suffix = self.settings.EXECUTOR_RM_SUFFIX
        self.executor_get_suffix = self.settings.EXECUTOR_GET_SUFFIX

    @property
    def executor_service(self):
        """Executor service"""
        return ExecutorService()

    @property
    def task_service(self):
        """Task service"""
        return TaskService()

    @property
    def request_session(self):
        """Request session"""
        return RequestWithHttpx()

    async def _run(self):
        """Run"""
        logger.info('Check life cycle task is running')
        while True:
            if not self._server_running:
                break
            executors = await self.get_executors()
            for executor in executors:
                # 遍历获取每一个执行器的信息
                if executor.status == Status.ONLINE.value:
                    task_count = 0
                    # 请求
                    containers = await self.get_all_containers(executor.url)
                    for container in containers:
                        if container.status == Status.RUNNING.name:
                            task_count += 1
                        else:
                            # 数据更新
                            status = Status[container.status].value
                            await self.update_task_record(task_name=container.task_name,
                                                          status=status,  # noqa
                                                          task_end_time=datetime.now())
                            await self.update_server_task_record(task_name=container.task_name,
                                                                 task_status=status)  # noqa
                            await self.remove_container(url=executor.url, container_id=container.container_id)
                            logger.info("Completed task %s life cycle", container.task_name)
                    await self.update_task_count(pk=executor.id, task_count=task_count)
                    logger.debug("Executor %s task count is %d", executor.id, task_count)
            await asyncio.sleep(20)
        logger.info('Check life cycle task is stopped')

    @session_ctx
    async def get_executors(self) -> list[ExecutorSchema]:
        """
        Get all executors
        获取保持心跳的执行器
        :return:
        """
        return await self.executor_service.get(search_fields={'status': Status.ONLINE.value})  # noqa

    async def get_all_containers(self, url: str) -> list[ContainerSchema]:
        """
        Get exited containers
        :param url:
        :return:
        """
        resp = await self.request_session.request('GET', url + self.executor_get_suffix)
        return [ContainerSchema.parse_obj(i) for i in resp.get('data')]

    async def remove_container(self, url: str, container_id: str):
        """Remove container from remote executor"""
        return await self.request_session.request('GET', url + self.executor_rm_url_suffix % container_id)

    @session_ctx
    async def update_task_record(self, task_name: str, status: int, task_end_time: datetime) -> TaskSchema:
        """
        Update task record
        :param task_name:
        :param status:
        :param task_end_time:
        :return:
        """
        # 主要字段为 status 和 task_end_time
        obj_in = dict(status=status, task_end_time=task_end_time.strftime('%Y-%m-%d %H:%M:%S'))
        return await self.task_service.update_by_name(name=task_name, obj_in=obj_in)

    @session_ctx
    async def update_task_count(self, pk: int, task_count: int):
        """
        Update executor task count
        :param pk:
        :param task_count:
        :return:
        """
        await self.executor_service.update(pk=pk, obj_in={'task_count': task_count})

    async def update_server_task_record(self, task_name: str, task_status: int) -> dict:
        """
        Update server task record
        :param task_name:
        :param task_status:
        :return:
        """
        # 先根据task_name获取id
        resp = await self.request_session.request('GET', self.server_task_url,
                                                  params={'query': 'filter_name=' + task_name})
        # 再进行更新
        task = resp.get('data')
        if task:
            data = {'task_status': task_status}
            return await self.request_session.request('PATCH', self.server_task_crud_url % task[0].get('id'), json=data)

    async def server_start(self, **_):
        """Server start"""
        if self._server_running is None:
            logger.debug('Change %s.server_running to "True"', self.__class__.name)
            self._server_running = True

    async def check_executor_task(self, **_):
        """Task"""
        self.life_cycle = asyncio.create_task(self._run())

    async def server_stop(self, **_):
        """Server stop"""
        logger.debug('Change %s.server_running to "False"', self.__class__.name)
        self._server_running = False
        if self.life_cycle and not self.life_cycle.done():
            self.life_cycle.cancel('server stop!')
