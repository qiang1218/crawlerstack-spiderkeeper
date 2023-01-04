"""
StorageServer schema
"""
from pydantic import (BaseModel, constr)  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_server.schemas.base import InDBMixin


class StorageServerBase(BaseModel):
    """StorageServer base schema."""
    name: constr(max_length=200) = None
    url: constr(max_length=200) = None
    storage_class: constr(max_length=200) = None


class StorageServerSchema(StorageServerBase, InDBMixin):
    """StorageServer model schema."""


class StorageServerCreate(StorageServerBase):
    """StorageServer create schema."""
    name: constr(max_length=200)
    url: constr(max_length=200)
    storage_class: constr(max_length=200)


class StorageServerUpdate(StorageServerBase):
    """StorageServer update schema."""
