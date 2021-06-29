"""
Schedule schema.
"""
from datetime import datetime

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper.schemas.base import InDBMixin


class ScheduleBase(BaseModel):
    """Base schedule schema."""
    next_time: datetime


class Schedule(ScheduleBase, InDBMixin):
    """Schedule model schema."""
    job_id: int


class ScheduleCreate:
    """Schedule create schema."""
    job_id: int


class ScheduleUpdate:
    """Schedule update schema."""
