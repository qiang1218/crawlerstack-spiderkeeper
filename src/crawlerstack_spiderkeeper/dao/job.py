"""
Jbo dao.
"""
from typing import Optional

from sqlalchemy import select

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db.models import Job, Task
from crawlerstack_spiderkeeper.schemas.job import JobCreate, JobUpdate
from crawlerstack_spiderkeeper.utils.states import States


class JobDAO(BaseDAO[Job, JobCreate, JobUpdate]):
    """
    Job dao.
    """
    model = Job

    async def state(self, *, pk: int) -> Optional[States]:
        """
        Job state.
        :param pk:
        :return:
        """
        stmt = select(Task).filter(Task.job_id == pk).order_by(Task.id.desc())

        obj: Task = await self.session.scalar(stmt)
        if obj:
            return States(obj.state)
