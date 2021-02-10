from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr

from crawlerstack_spiderkeeper.schemas.base import InDBMixin


class AuditBase(BaseModel):
    url: constr(max_length=300)
    method: constr(max_length=10)
    client: constr(max_length=150)
    detail: str


class Audit(AuditBase, InDBMixin):
    datetime: datetime
    user_id: Optional[int] = None


class AuditCreate(AuditBase):
    user_id: Optional[int] = None


class AuditUpdate(AuditBase):
    pass
