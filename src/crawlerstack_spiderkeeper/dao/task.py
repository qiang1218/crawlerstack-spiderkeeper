"""
Task dao.
"""
from typing import List, Optional

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db import ScopedSession as Session
from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.schemas.task import TaskCreate, TaskUpdate
from crawlerstack_spiderkeeper.utils import scoping_session
from crawlerstack_spiderkeeper.utils.states import States

# pylint: disable=no-member

class TaskDAO(BaseDAO[Task, TaskCreate, TaskUpdate]):
    """
    Task dao.
    """

    @scoping_session
    def get_running(
            self,
            job_id: Optional[int] = None,
            skip: Optional[int] = 0,
            limit: Optional[int] = 100
    ) -> List[Task]:
        """
        Get running task list.
        :param job_id:
        :param skip:
        :param limit:
        :return:
        """
        condition = {'state': States.Running.value}
        if job_id:
            condition.update({'job_id': job_id})
        return Session.query(self.model).filter_by(**condition).offset(skip).limit(limit).all()

    @scoping_session
    def count_running_task(self, job_id: Optional[int]) -> int:
        """
        Get running task count.
        :param job_id:
        :return:
        """
        condition = {'state': States.Running.value}
        if job_id:
            condition.update({'job_id': job_id})
        return Session.query(self.model).filter_by(**condition).count()

    @scoping_session
    def increase_item_count(self, pk: int) -> Task:
        """
        Increase item count.
        :param pk:
        :return:
        """
        obj: Task = self.get(pk)
        obj.item_count += 1
        Session.add(obj)
        Session.commit()
        Session.refresh(obj)
        return obj
