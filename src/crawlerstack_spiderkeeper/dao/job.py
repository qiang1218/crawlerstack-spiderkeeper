"""
Jbo dao.
"""
from sqlalchemy import select

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db.models import Job, Task
from crawlerstack_spiderkeeper.schemas.job import JobCreate, JobUpdate
from crawlerstack_spiderkeeper.utils.status import Status


class JobDAO(BaseDAO[Job, JobCreate, JobUpdate]):
    """
    Job dao.
    """
    model = Job

    async def status(self, *, pk: int) -> None | Status:
        """
        Job status.

        通过获取 Job 下的所有 Task 判断 Job 是否在运行。
        :param pk:
        :return:
        """
        stmt = select(Task).filter(Task.job_id == pk).order_by(Task.id.desc())

        obj: Task = await self.session.scalar(stmt)
        if obj:
            return Status(obj.status)
