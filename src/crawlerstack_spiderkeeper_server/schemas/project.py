"""
Project schema
"""
from pydantic import (BaseModel, constr)  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_server.schemas.base import InDBMixin


class ProjectBase(BaseModel):
    """Project base schema."""
    name: constr(max_length=200) = None
    desc: constr(max_length=200) = None


class ProjectSchema(ProjectBase, InDBMixin):
    """Project model schema."""


class ProjectCreate(ProjectBase):
    """Project create schema."""
    name: constr(max_length=200)
    desc: constr(max_length=200)


class ProjectUpdate(ProjectBase):
    """Project update schema."""
