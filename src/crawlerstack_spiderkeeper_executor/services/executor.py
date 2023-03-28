"""executor service"""
import logging

from crawlerstack_spiderkeeper_executor.config import settings
from crawlerstack_spiderkeeper_executor.executor import executor_factory
from crawlerstack_spiderkeeper_executor.schemas.base import TaskSchema
from crawlerstack_spiderkeeper_executor.utils.exceptions import (
    ContainerRmError, ContainerStopError, RemoteTaskCheckError,
    RemoteTaskGetError, RemoteTaskRunError)
from crawlerstack_spiderkeeper_executor.utils.status import ContainerStatus

logger = logging.getLogger(__name__)


class ExecutorService:
    """executor service"""

    def __init__(self):
        self.executor_cls = executor_factory()

    @property
    def executor(self):
        """executor"""
        return self.executor_cls(settings)

    async def get(self) -> list:
        """
        get all active containers
        :return:
        """
        try:
            datas = await self.executor.get()
            # 统一进行状态码转换
            for i in datas:
                status = i.get('status')
                i['status'] = ContainerStatus[status].value
            return datas
        except Exception as ex:
            logger.warning("Get active containers failed: %s", ex)
        raise RemoteTaskGetError()

    async def run(self, obj_in: TaskSchema) -> str:
        """
        run
        :param obj_in:
        :return:
        """
        try:
            return await self.executor.run(obj_in)
        except Exception as ex:
            logger.warning("Task run failed: %s", ex)
        raise RemoteTaskRunError()

    async def check_by_id(self, container_id: str) -> str:
        """
        check by id
        status=(created	restarting running	paused	exited	dead)
        :param container_id:
        :return:
        """
        try:
            status = await self.executor.status(container_id)
            return ContainerStatus[status].value  # noqa
        except Exception as ex:
            logger.warning("Task check failed: %s", ex)
        raise RemoteTaskCheckError()

    async def rm_by_id(self, container_id: str) -> None:
        """
        rm by id
        :param container_id:
        :return:
        """
        try:
            return await self.executor.delete(container_id)
        except Exception as ex:
            logger.warning("Container rm failed: %s", ex)
        raise ContainerRmError()

    async def stop_by_id(self, container_id: str) -> None:
        """
        stop by id
        :param container_id:
        :return:
        """
        try:
            return await self.executor.stop(container_id)
        except Exception as ex:
            logger.warning("Container stop failed: %s", ex)
        raise ContainerStopError()
