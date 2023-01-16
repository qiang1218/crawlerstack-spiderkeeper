"""
Executor schema
"""
from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_scheduler.schemas.base import InDBMixin
from crawlerstack_spiderkeeper_scheduler.utils.status import Status


class ExecutorBase(BaseModel):
    """Executor base schema."""
    name: constr(max_length=200) = None
    selector: constr(max_length=200) = None
    url: constr(max_length=200) = None
    type: constr(max_length=200) = None
    status: int = None
    memory: int = 0
    cpu: int = 0
    task_count: int = 0


class ExecutorSchema(ExecutorBase, InDBMixin):
    """Executor model schema."""


class ExecutorCreate(ExecutorBase):
    """Executor create schema."""
    name: constr(max_length=200)
    url: constr(max_length=200)
    type: constr(max_length=200)


class ExecutorUpdate(ExecutorBase):
    """Executor update schema."""
    status: int = Status.ONLINE.value
