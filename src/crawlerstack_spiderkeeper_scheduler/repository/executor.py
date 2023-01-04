"""Executor"""
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_scheduler.repository.base import BaseRepository

from crawlerstack_spiderkeeper_scheduler.models import Executor
from crawlerstack_spiderkeeper_scheduler.schemas.executor import (ExecutorCreate, ExecutorUpdate, ExecutorSchema,
                                                                  ExecutorAndDetailSchema)
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import ObjectDoesNotExist


class ExecutorRepository(BaseRepository[Executor, ExecutorCreate, ExecutorUpdate, ExecutorSchema]):
    """executor repository"""
    model = Executor
    model_schema = ExecutorSchema

    async def get_by_name(self, name: str) -> ExecutorSchema:
        """
        get by name
        :param name:
        :return:
        """

        stmt = select(self.model).where(self.model.name == name)
        obj = await self.session.scalar(stmt)
        if obj:
            return self.model_schema.from_orm(obj)
        raise ObjectDoesNotExist()

    async def get_by_type_join_detail(self, executor_type: str, status: int) -> List[ExecutorAndDetailSchema]:
        """
        get by executor type join detail
        :param executor_type:
        :param status:
        :return:
        """
        stmt = select(self.model).filter(self.model.type == executor_type, self.model.status == status).options(
            selectinload(self.model.executor_detail))
        objs = await self.session.scalar(stmt)
        results = objs.scalars().all()
        if not results:
            raise ObjectDoesNotExist()
        return [ExecutorAndDetailSchema.from_orm(obj) for obj in results]

