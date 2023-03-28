"""
Task schema
"""
from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_server.schemas.base import InDBMixin


class TaskBase(BaseModel):
    """Task base schema."""
    name: constr(max_length=200) = None
    job_id: int = None
    task_status: int = None
    consume_status: int = None


class TaskSchema(TaskBase, InDBMixin):
    """Task model schema."""


class TaskCreate(TaskBase):
    """Task create schema."""
    name: constr(max_length=200)
    job_id: int


class TaskUpdate(TaskBase):
    """Task update schema."""
