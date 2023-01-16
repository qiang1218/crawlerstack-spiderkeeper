"""
Artifact schema
"""
from datetime import datetime

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_server.schemas.base import InDBMixin


class ArtifactBase(BaseModel):
    """Project base schema."""
    name: constr(max_length=200) = None
    desc: constr(max_length=2000) = None
    image: str = None
    tag: str = None
    version: str = 'latest'
    project_id: int = None


class ArtifactSchema(ArtifactBase, InDBMixin):
    """Artifact model schema."""


class ArtifactCreate(ArtifactBase):
    """Artifact create schema."""
    name: constr(max_length=200)
    desc: constr(max_length=2000)
    image: str
    project_id: int


class ArtifactUpdate(ArtifactBase):
    """Artifact update schema."""
