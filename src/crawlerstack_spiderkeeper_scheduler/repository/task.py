"""task"""

from crawlerstack_spiderkeeper_scheduler.repository.base import BaseRepository

from crawlerstack_spiderkeeper_scheduler.models import Task
from crawlerstack_spiderkeeper_scheduler.schemas.task import (TaskCreate, TaskUpdate, TaskSchema)


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate, TaskSchema]):
    """task"""
    model = Task
    model_schema = TaskSchema
