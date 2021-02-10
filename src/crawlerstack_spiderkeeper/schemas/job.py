from datetime import datetime

from pydantic import BaseModel, constr

from crawlerstack_spiderkeeper.schemas.base import InDBMixin


class JobBase(BaseModel):
    name: constr(max_length=200) = None
    cmdline: constr(max_length=500) = None

    storage_enable: bool = False

    server_id: int = None
    artifact_id: int = None


class Job(JobBase, InDBMixin):
    artifact_id: int
    name: constr(max_length=200)
    create_time: datetime
    update_time: datetime


class JobCreate(JobBase):
    artifact_id: int
    server_id: int
    name: constr(max_length=200)
    cmdline: constr(max_length=500)


class JobUpdate(JobBase):
    pass
