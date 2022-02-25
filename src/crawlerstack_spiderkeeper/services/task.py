"""
Task service
"""
from crawlerstack_spiderkeeper.dao import TaskDAO
from crawlerstack_spiderkeeper.db.models import Task
from crawlerstack_spiderkeeper.schemas.task import TaskCreate
from crawlerstack_spiderkeeper.services.base import EntityService


class TaskService(EntityService):
    """
    Task service.
    """
    DAO_CLASS = TaskDAO
    #
    # async def create(
    #         self,
    #         *,
    #         obj_in: TaskCreate
    # ) -> Task:
    #     return await self.dao.create(obj_in=TaskCreate(job_id=1))
