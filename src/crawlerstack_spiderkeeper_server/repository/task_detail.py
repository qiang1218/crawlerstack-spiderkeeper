"""task detail"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_server.repository.base import BaseRepository

from crawlerstack_spiderkeeper_server.models import Task, TaskDetail
from crawlerstack_spiderkeeper_server.schemas.task_detail import (TaskDetailCreate, TaskDetailUpdate, TaskDetailSchema)
from crawlerstack_spiderkeeper_server.utils.exceptions import ObjectDoesNotExist


class TaskDetailRepository(BaseRepository[TaskDetail, TaskDetailCreate, TaskDetailUpdate, TaskDetailSchema]):
    """
    job repository
    """
    model = TaskDetail
    model_schema = TaskDetailSchema

    async def get_task_detail_from_task_name(self, task_name: str):
        """
        get task detail from task name
        :param task_name:
        :return:
        """
        stmt = select(Task).filter(Task.name == task_name).options(selectinload(Task.task_details))
        task: Task = await self.session.scalar(stmt)
        if not task:
            # Task does not exist
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(task.task_details)
