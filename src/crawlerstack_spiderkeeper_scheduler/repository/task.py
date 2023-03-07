"""task"""
from sqlalchemy import select

from crawlerstack_spiderkeeper_scheduler.models import Task
from crawlerstack_spiderkeeper_scheduler.repository.base import BaseRepository
from crawlerstack_spiderkeeper_scheduler.schemas.task import (TaskCreate,
                                                              TaskSchema,
                                                              TaskUpdate)
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    ObjectDoesNotExist


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate, TaskSchema]):
    """task"""
    model = Task
    model_schema = TaskSchema

    async def get_by_name(self, name: str) -> TaskSchema:
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
