"""Executor"""

from sqlalchemy import select

from crawlerstack_spiderkeeper_scheduler.models import Executor
from crawlerstack_spiderkeeper_scheduler.repository.base import BaseRepository
from crawlerstack_spiderkeeper_scheduler.schemas.executor import (
    ExecutorCreate, ExecutorSchema, ExecutorUpdate)
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    ObjectDoesNotExist


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
