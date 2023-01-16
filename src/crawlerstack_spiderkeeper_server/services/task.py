"""Task"""
from typing import Any, Dict, Union

from crawlerstack_spiderkeeper_server.models import Task
from crawlerstack_spiderkeeper_server.repository.job import JobRepository
from crawlerstack_spiderkeeper_server.repository.task import TaskRepository
from crawlerstack_spiderkeeper_server.schemas.job import JobSchema
from crawlerstack_spiderkeeper_server.schemas.task import (TaskCreate,
                                                           TaskSchema,
                                                           TaskUpdate)
from crawlerstack_spiderkeeper_server.services.base import EntityService
from crawlerstack_spiderkeeper_server.utils.types import (CreateSchemaType,
                                                          ModelSchemaType,
                                                          UpdateSchemaType)


class TaskService(EntityService[Task, TaskCreate, TaskUpdate, TaskSchema]):
    """
    Task service.
    """
    REPOSITORY_CLASS = TaskRepository

    @property
    def job_repository(self):
        return JobRepository()

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
        await self.job_repository.exists(obj_in.job_id)
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
        job_id = obj_in.job_id
        if job_id is not None:
            await self.job_repository.exists(obj_in.job_id)
        return await self.repository.update_by_id(pk=pk, obj_in=obj_in)

    async def get_job_from_task_id(self, pk: int) -> JobSchema:
        """
        get a job from task id
        :param pk:
        :return:
        """
        return await self.job_repository.get_job_from_task_id(pk)
