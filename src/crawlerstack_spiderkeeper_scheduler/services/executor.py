"""Executor"""

from crawlerstack_spiderkeeper_scheduler.models import Executor
from crawlerstack_spiderkeeper_scheduler.repository.executor import \
    ExecutorRepository
from crawlerstack_spiderkeeper_scheduler.schemas.executor import (
    ExecutorCreate, ExecutorSchema, ExecutorUpdate)
from crawlerstack_spiderkeeper_scheduler.services.base import EntityService
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    ObjectDoesNotExist
from crawlerstack_spiderkeeper_scheduler.utils.types import (CreateSchemaType,
                                                             ModelSchemaType,
                                                             UpdateSchemaType)


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
        # 同时创建 executor_detail表，创建时候，旧表置默认值
        try:
            executor = await self.repository.get_by_name(obj_in.name)
            obj = await self.repository.update_by_id(pk=executor.id, obj_in=obj_in)
            return obj
        except ObjectDoesNotExist:
            obj = await self.repository.create(obj_in=obj_in)
            return obj

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
