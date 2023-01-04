"""Task"""
from typing import Union, Dict, Any

from crawlerstack_spiderkeeper_scheduler.repository.executor import ExecutorRepository
from crawlerstack_spiderkeeper_scheduler.services.base import EntityService
from crawlerstack_spiderkeeper_scheduler.models import Task
from crawlerstack_spiderkeeper_scheduler.schemas.task import (TaskCreate, TaskUpdate, TaskSchema)
from crawlerstack_spiderkeeper_scheduler.repository.task import TaskRepository

from crawlerstack_spiderkeeper_server.utils.types import CreateSchemaType, ModelSchemaType, UpdateSchemaType


class TaskService(EntityService[Task, TaskCreate, TaskUpdate, TaskSchema]):
    """
    Task service.
    """
    REPOSITORY_CLASS = TaskRepository

    @property
    def executor_repository(self):
        return ExecutorRepository()

    async def create(
            self,
            *,
            obj_in: CreateSchemaType
    ) -> ModelSchemaType:
        """
        Create a record.
        :param obj_in:
        :return:
        """
        await self.executor_repository.exists(obj_in.executor_id)
        return await self.repository.create(obj_in=obj_in)

    async def update_by_id(
            self,
            pk: int,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelSchemaType:
        """
        Update a record.
        :param pk:
        :param obj_in:
        :return:
        """
        # 局部更新时
        executor_id = obj_in.executor_id
        if executor_id is not None:
            await self.executor_repository.exists(obj_in.executor_id)
        return await self.repository.update_by_id(pk=pk, obj_in=obj_in)
