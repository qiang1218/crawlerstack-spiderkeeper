"""task"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_server.models import Job, Task, TaskDetail
from crawlerstack_spiderkeeper_server.repository.base import BaseRepository
from crawlerstack_spiderkeeper_server.schemas.task import (TaskCreate,
                                                           TaskSchema,
                                                           TaskUpdate)
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate, TaskSchema]):
    """
    job repository
    """
    model = Task
    model_schema = TaskSchema

    async def get_task_from_task_detail_id(self, task_detail_id: int) -> TaskSchema:
        """
        Get job from task id
        :param task_detail_id:
        :return:
        """
        stmt = select(TaskDetail).filter(TaskDetail.id == task_detail_id).options(selectinload(TaskDetail.task))
        task_detail: TaskDetail = await self.session.scalar(stmt)
        if not task_detail:
            # Task does not exist
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(task_detail.task)
