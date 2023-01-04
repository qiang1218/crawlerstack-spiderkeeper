"""Executor"""
from typing import List

from crawlerstack_spiderkeeper_scheduler.services.base import EntityService
from crawlerstack_spiderkeeper_scheduler.models import Executor
from crawlerstack_spiderkeeper_scheduler.schemas.executor import (ExecutorCreate, ExecutorUpdate, ExecutorSchema,
                                                                  ExecutorAndDetailSchema)
from crawlerstack_spiderkeeper_scheduler.repository.executor import ExecutorRepository
from crawlerstack_spiderkeeper_scheduler.utils.types import CreateSchemaType, UpdateSchemaType, ModelSchemaType

from crawlerstack_spiderkeeper_scheduler.utils.exceptions import ObjectDoesNotExist


class ExecutorService(EntityService[Executor, ExecutorCreate, ExecutorUpdate, ExecutorSchema]):
    """
    Executor service.
    """
    REPOSITORY_CLASS = ExecutorRepository

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
        # 创建部分需要特殊处理, 考虑到executor_name的全局唯一性， 默认状态为离线，需由心跳将状态置为在线
        try:
            executor = await self.repository.get_by_name(obj_in.name)
            return await self.repository.update_by_id(pk=executor.id, obj_in=obj_in)
        except ObjectDoesNotExist:
            return await self.repository.create(obj_in=obj_in)

    async def heartbeat(
            self,
            *,
            pk: int,
            obj_in: UpdateSchemaType
    ) -> ModelSchemaType:
        """
        heartbeat
        :param pk:
        :param obj_in:
        :return:
        """
        return await self.repository.update_by_id(pk=pk, obj_in=obj_in)

    async def get_by_type_join_detail(self, executor_type: str, status: int) -> List[ExecutorAndDetailSchema]:
        """
        get by type join detail
        :param executor_type:
        :param status:
        :return:
        """
        return await self.get_by_type_join_detail(executor_type=executor_type, status=status)
