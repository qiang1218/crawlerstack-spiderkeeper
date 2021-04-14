"""
Audit schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper.schemas.base import InDBMixin


class AuditBase(BaseModel):
    """Base audit schema"""
    url: constr(max_length=300)
    method: constr(max_length=10)
    client: constr(max_length=150)
    detail: str


class Audit(AuditBase, InDBMixin):
    """Audit model schema."""
    datetime: datetime
    user_id: Optional[int] = None


class AuditCreate(AuditBase):
    """Audit create schema"""
    user_id: Optional[int] = None


class AuditUpdate(AuditBase):
    """Audit update schema."""
