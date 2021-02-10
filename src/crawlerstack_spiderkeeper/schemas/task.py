from datetime import datetime

from pydantic import BaseModel, constr

from crawlerstack_spiderkeeper.schemas.base import InDBMixin
from crawlerstack_spiderkeeper.utils.states import States


class TaskBase(BaseModel):
    create_time: datetime = None
    update_time: datetime = None
    state: States = None
    item_count: int = 0
    detail: str = None
    container_id: constr(max_length=120) = None


class Task(TaskBase, InDBMixin):
    create_time: datetime
    update_time: datetime
    job_id: int = None


class TaskCreate(TaskBase):
    job_id: int


class TaskUpdate(TaskBase):
    item_count: int = None
