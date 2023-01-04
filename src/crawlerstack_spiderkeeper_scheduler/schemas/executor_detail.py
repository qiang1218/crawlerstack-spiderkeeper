"""
Executor detailschema
"""
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_scheduler.schemas.base import InDBMixin


class ExecutorDetailBase(BaseModel):
    """Executor base schema."""
    task_count: int = None
    executor_id: int = None


class ExecutorDetailSchema(ExecutorDetailBase, InDBMixin):
    """Executor detail model schema."""


class ExecutorDetailCreate(ExecutorDetailBase):
    """Executor detail create schema."""
    executor_id: int


class ExecutorDetailUpdate(ExecutorDetailBase):
    """Executor detail update schema."""
    task_count: int
