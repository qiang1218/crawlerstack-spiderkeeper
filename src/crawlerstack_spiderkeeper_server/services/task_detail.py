"""Task detail"""
from typing import Union, Dict, Any

from crawlerstack_spiderkeeper_server.schemas.job import JobSchema
from crawlerstack_spiderkeeper_server.schemas.task import TaskSchema
from crawlerstack_spiderkeeper_server.services.base import EntityService
from crawlerstack_spiderkeeper_server.models import TaskDetail
from crawlerstack_spiderkeeper_server.schemas.task_detail import (TaskDetailCreate, TaskDetailUpdate, TaskDetailSchema)
from crawlerstack_spiderkeeper_server.repository.task_detail import TaskDetailRepository
from crawlerstack_spiderkeeper_server.repository.task import TaskRepository
from crawlerstack_spiderkeeper_server.utils.types import CreateSchemaType, ModelSchemaType, UpdateSchemaType


class TaskDetailService(EntityService[TaskDetail, TaskDetailCreate, TaskDetailUpdate, TaskDetailSchema]):
    """
    Task detail service.
    """
    REPOSITORY_CLASS = TaskDetailRepository

    @property
    def task_repository(self):
        return TaskRepository()

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
        await self.task_repository.exists(obj_in.task_id)
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
        task_id = obj_in.task_id
        if task_id is not None:
            await self.task_repository.exists(obj_in.task_id)
        return await self.repository.update_by_id(pk=pk, obj_in=obj_in)

    async def get_task_from_task_detail_id(self, pk: int) -> TaskSchema:
        """
        get a job from task id
        :param pk:
        :return:
        """
        return await self.task_repository.get_task_from_task_detail_id(pk)
