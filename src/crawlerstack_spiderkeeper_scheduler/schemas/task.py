"""
Task schema
"""
from datetime import datetime

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_scheduler.schemas.base import InDBMixin


class TaskBase(BaseModel):
    """Task base schema."""
    name: constr(max_length=200) = None
    url: constr(max_length=200) = None
    type: constr(max_length=200) = None
    status: int = None
    executor_id: int = None
    container_id: constr(max_length=200) = None
    task_start_time: datetime = None
    task_end_time: datetime = None


class TaskSchema(TaskBase, InDBMixin):
    """task model schema."""


class TaskCreate(TaskBase):
    """Task create schema."""
    name: constr(max_length=200)
    url: constr(max_length=200)
    type: constr(max_length=200)
    status: int
    executor_id: int
    container_id: constr(max_length=200)


class TaskUpdate(TaskBase):
    """Task update schema."""
    status: int
    task_end_time: datetime
