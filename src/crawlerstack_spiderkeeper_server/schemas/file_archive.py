"""
FileArchive schema
"""
from datetime import datetime

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_server.schemas.base import InDBMixin


class FileArchiveBase(BaseModel):
    """FileArchive base schema."""
    name: constr(max_length=100) = None
    local_path: constr(max_length=200) = None
    key: constr(max_length=200) = None
    storage_name: constr(max_length=100) = None
    storage_url: constr(max_length=200) = None
    status: bool = False
    expired_time: datetime = None


class FileArchiveSchema(FileArchiveBase, InDBMixin):
    """FileArchive model schema."""


class FileArchiveCreate(FileArchiveBase):
    """Project create schema."""
    name: constr(max_length=100)
    local_path: constr(max_length=200)
    key: constr(max_length=200)
    storage_name: constr(max_length=100)
    storage_url: constr(max_length=200)
    expired_time: datetime


class FileArchiveUpdate(FileArchiveBase):
    """FileArchive update schema."""
    expired_time: datetime
