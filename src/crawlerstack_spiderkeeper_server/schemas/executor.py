"""
Executor schema
"""
from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_server.schemas.base import InDBMixin


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
    expired_time: int = None


class ExecutorSchema(ExecutorBase, InDBMixin):
    """Executor model schema."""
