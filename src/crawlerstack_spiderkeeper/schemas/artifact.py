"""
Artifact schema.
"""
from datetime import datetime

from fastapi import UploadFile
from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper.schemas.base import InDBMixin


class ArtifactBase(BaseModel):
    """
    Base artifact schema.
    """
    status: int = None
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


class ArtifactFileCreate(ArtifactBase):
    """
    Artifact create schema
    """
    file: UploadFile
    project_id: int
    project_id: int


class ArtifactUpdate(ArtifactBase):
    """Artifact update schema"""
