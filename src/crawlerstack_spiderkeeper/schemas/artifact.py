"""
Artifact schema.
"""
from datetime import datetime

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper.schemas.base import InDBMixin
from crawlerstack_spiderkeeper.utils.states import States


class ArtifactBase(BaseModel):
    """
    Base artifact schema.
    """
    state: int = None
    filename: constr(max_length=200) = None
    interpreter: constr(max_length=500) = None
    execute_path: constr(max_length=100) = None
    tag: constr(max_length=100) = None


class Artifact(ArtifactBase, InDBMixin):
    """
    Artifact model schema
    """
    create_time: datetime = None
    project_id: int = None


class ArtifactCreate(ArtifactBase):
    """
    Artifact create schema
    """
    filename: constr(max_length=200)
    project_id: int


class ArtifactUpdate(ArtifactBase):
    """Artifact update schema"""
