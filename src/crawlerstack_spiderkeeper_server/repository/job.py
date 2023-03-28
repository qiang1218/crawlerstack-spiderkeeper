"""job"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_server.models import Job, Task
from crawlerstack_spiderkeeper_server.repository.base import BaseRepository
from crawlerstack_spiderkeeper_server.schemas.job import (JobCreate, JobSchema,
                                                          JobUpdate)
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist


class JobRepository(BaseRepository[Job, JobCreate, JobUpdate, JobSchema]):
    """
    job repository
    """
    model = Job
    model_schema = JobSchema

    async def get_job_from_task_id(self, task_id: int) -> JobSchema:
        """
        Get job from task id
        :param task_id:
        :return:
        """
        stmt = select(Task).filter(Task.id == task_id).options(selectinload(Task.job))
        task: Task = await self.session.scalar(stmt)
        if not task:
            # Task does not exist
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(task.job)

    async def get_job_from_task_name(self, task_name: str) -> JobSchema:
        """
        Get job from task name
        :param task_name:
        :return:
        """
        stmt = select(Task).filter(Task.name == task_name).options(selectinload(Task.job))
        task: Task = await self.session.scalar(stmt)
        if not task:
            # Task does not exist
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(task.job)
