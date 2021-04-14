"""
Storage schema
"""
from datetime import datetime

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper.schemas.base import InDBMixin
from crawlerstack_spiderkeeper.utils.states import States


class StorageBase(BaseModel):
    """Storage base schema."""
    create_time: datetime = None
    update_time: datetime = None
    count: int = 0
    state: States = None
    detail: constr(max_length=500) = None


class Storage(StorageBase, InDBMixin):
    """Storage model schema."""
    create_time: datetime
    update_time: datetime
    job_id: int = 0
    status: constr(max_length=45)


class StorageCreate(StorageBase):
    """Storage create schema."""
    job_id: int
    state: States


class StorageUpdate(StorageBase):
    """Storage update schema."""
    count: int = None
