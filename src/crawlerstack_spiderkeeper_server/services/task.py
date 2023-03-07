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
from crawlerstack_spiderkeeper_server.signals import (data_task_clear,
                                                      data_task_start,
                                                      data_task_terminate)
from crawlerstack_spiderkeeper_server.utils.exceptions import TaskActionError
from crawlerstack_spiderkeeper_server.utils.status import Status
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
        """Job repository"""
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
        # 创建消费者
        await data_task_start.send(task_name=obj_in.name)
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
        Get a job from task id
        :param pk:
        :return:
        """
        return await self.job_repository.get_job_from_task_id(pk)

    async def get_by_name(
            self,
            name: str,
    ) -> ModelSchemaType:
        """
        Get a record by name.
        :param name:
        :return:
        """
        return await self.repository.get_by_name(name)

    async def start_task_consume(self, pk: int) -> str:
        """
        Start task consume
        :param pk:
        :return:
        """
        obj = await self.repository.get_by_id(pk)
        if obj.consume_status == Status.STOPPED.value:
            await data_task_start.send(task_name=obj.name)
            await self.repository.update_by_id(pk=pk,
                                               obj_in=TaskUpdate(
                                                   consume_status=Status.RUNNING.value  # noqa
                                               ))
            return 'Start task consume success'
        raise TaskActionError('Start task consume failed, consume status inconsistent')

    async def stop_task_consume(self, pk: int) -> str:
        """
        Stop task consume by id
        :param pk:
        :return:
        """
        # 判断当前消费的状态
        obj = await self.repository.get_by_id(pk)
        if obj.consume_status == Status.RUNNING.value:
            await data_task_clear.send(task_name=obj.name)
            await self.repository.update_by_id(pk=pk,
                                               obj_in=TaskUpdate(
                                                   consume_status=Status.STOPPED.value  # noqa
                                               ))
            return 'Stop task consume success'
        raise TaskActionError('Stop task consume failed, consume status inconsistent')

    async def terminate_task_consume(self, pk: int) -> str:
        """
        Terminate task consume
        :param pk:
        :return:
        """
        obj = await self.repository.get_by_id(pk)
        if obj.consume_status in (Status.RUNNING.value, Status.STOPPED.value):
            await data_task_terminate.send(task_name=obj.name)
            await self.repository.update_by_id(pk=pk,
                                               obj_in=TaskUpdate(
                                                   consume_status=Status.FINISH.value  # noqa
                                               ))
            return 'Terminate task consume success'
        raise TaskActionError('Terminate task consume failed, consume status inconsistent')
