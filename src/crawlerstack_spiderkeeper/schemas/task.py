"""
Task schema.
"""
from datetime import datetime

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper.schemas.base import InDBMixin


class TaskBase(BaseModel):
    """Task base schema."""
    create_time: datetime = None
    update_time: datetime = None
    status: int = None
    item_count: int = 0
    detail: str = None
    container_id: constr(max_length=120) = None


class Task(TaskBase, InDBMixin):
    """Task model schema."""
    create_time: datetime
    update_time: datetime
    job_id: int = None


class TaskCreate(TaskBase):
    """Task create schema."""
    job_id: int


class TaskUpdate(TaskBase):
    """Task update schema."""
    item_count: int = None
