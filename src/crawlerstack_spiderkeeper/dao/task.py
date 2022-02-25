"""
Task dao.
"""
from typing import List, Optional

from sqlalchemy import func, select

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.schemas.task import TaskCreate, TaskUpdate
from crawlerstack_spiderkeeper.utils.status import Status


class TaskDAO(BaseDAO[Task, TaskCreate, TaskUpdate]):
    """
    Task dao.
    """
    model = Task

    async def get_running(
            self,
            job_id: Optional[int] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 100
    ) -> List[Task]:
        """
        Get running task list.
        :param job_id:
        :param offset:
        :param limit:
        :return:
        """
        condition = {'status': Status.RUNNING.value}
        if job_id:
            condition.update({'job_id': job_id})
        stmt = select(self.model).filter_by(**condition).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_running_task(self, job_id: Optional[int] = None) -> int:
        """
        Get running task count.
        :param job_id:
        :return:
        """
        condition = {'status': Status.RUNNING.value}
        if job_id:
            condition.update({'job_id': job_id})
        stmt = select(func.count()).select_from(self.model).filter_by(**condition)
        return await self.session.scalar(stmt)

    async def increase_item_count(self, pk: int) -> Task:
        """
        Increase item count.
        :param pk:
        :return:
        """
        obj: Task = await self.get_by_id(pk)
        obj.item_count += 1
        return obj
