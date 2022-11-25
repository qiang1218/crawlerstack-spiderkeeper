"""
Server schema.
"""
from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper.schemas.base import InDBMixin


class ServerBase(BaseModel):
    """Base server schema."""
    name: str
    type: str
    uri: str
    enable: bool = False


class Server(ServerBase, InDBMixin):
    """Server model schema."""


class ServerCreate(ServerBase):
    """Server create schema."""
    name: constr(max_length=45)
    type: constr(max_length=45)
    uri: constr(max_length=100)


class ServerUpdate(ServerBase):
    """Server update schema."""
    name: constr(max_length=45) = None
    type: constr(max_length=45) = None
    uri: constr(max_length=100) = None
    enable: bool = None
