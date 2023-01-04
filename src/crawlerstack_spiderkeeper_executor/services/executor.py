"""executor service"""
import logging

from crawlerstack_spiderkeeper_executor.executor import executor_factory

from crawlerstack_spiderkeeper_executor.schemas.base import TaskSchema
from crawlerstack_spiderkeeper_executor.utils.exceptions import RemoteTaskRunError, RemoteTaskCheckError, \
    ContainerRmError

logger = logging.getLogger(__name__)


class ExecutorService:

    def __init__(self, ):
        self.executor_cls = executor_factory()
        self.logger = logger

    @property
    def executor(self):
        """executor"""
        return self.executor_cls()

    async def run(self, obj_in: TaskSchema):
        """
        run
        :param obj_in:
        :return:
        """
        try:
            return await self.executor.run(obj_in)
        except Exception as e:
            self.logger.warning("Task run failed: %s", e)
        raise RemoteTaskRunError()

    async def check_by_id(self, container_id: str):
        """
        check by id
        status=(created	restarting running	paused	exited	dead)
        :param container_id:
        :return:
        """
        try:
            return await self.executor.status(container_id)
        except Exception as e:
            self.logger.warning("Task check failed: %s", e)
        raise RemoteTaskCheckError()

    async def rm_by_id(self, container_id: str):
        """
        rm by id
        :param container_id:
        :return:
        """
        try:
            await self.executor.delete(container_id)
        except Exception as e:
            self.logger.warning("Container rm failed: %s", e)
        raise ContainerRmError()
