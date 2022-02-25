"""
Storage schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper.schemas.base import InDBMixin
from crawlerstack_spiderkeeper.utils.status import Status


class StorageBase(BaseModel):
    """Storage base schema."""
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    count: int = 0
    state: int = None
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
    status: Status


class StorageUpdate(StorageBase):
    """Storage update schema."""
    count: Optional[int] = None
