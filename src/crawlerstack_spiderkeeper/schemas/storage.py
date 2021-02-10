from datetime import datetime

from pydantic import BaseModel, constr

from crawlerstack_spiderkeeper.schemas.base import InDBMixin
from crawlerstack_spiderkeeper.utils.states import States


class StorageBase(BaseModel):
    create_time: datetime = None
    update_time: datetime = None
    count: int = 0
    state: States = None
    detail: constr(max_length=500) = None


class Storage(StorageBase, InDBMixin):
    create_time: datetime
    update_time: datetime
    job_id: int = 0
    status: constr(max_length=45)


class StorageCreate(StorageBase):
    job_id: int
    state: States


class StorageUpdate(StorageBase):
    count: int = None
