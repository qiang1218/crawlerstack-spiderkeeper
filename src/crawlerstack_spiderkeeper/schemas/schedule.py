from datetime import datetime

from pydantic import BaseModel

from crawlerstack_spiderkeeper.schemas.base import InDBMixin


class ScheduleBase(BaseModel):
    next_time: datetime


class Schedule(ScheduleBase, InDBMixin):
    job_id: int


class ScheduleCreate:
    job_id: int


class ScheduleUpdate:
    """"""
