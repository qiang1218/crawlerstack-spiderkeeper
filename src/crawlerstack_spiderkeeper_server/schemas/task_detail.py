"""
TaskDetail schema
"""
from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_server.schemas.base import InDBMixin


class TaskDetailBase(BaseModel):
    """TaskDetail base schema."""
    task_id: int = None
    item_count: int = None
    detail: constr(max_length=100) = None


class TaskDetailSchema(TaskDetailBase, InDBMixin):
    """TaskDetail model schema."""


class TaskDetailCreate(TaskDetailBase):
    """TaskDetail create schema."""
    task_id: int


class TaskDetailUpdate(TaskDetailBase):
    """TaskDetail update schema."""
    item_count: int
