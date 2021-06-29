"""
Audit service.
"""


from crawlerstack_spiderkeeper.dao import audit_dao
from crawlerstack_spiderkeeper.schemas.audit import (Audit, AuditCreate,
                                                     AuditUpdate)
from crawlerstack_spiderkeeper.services.base import BaseService


class AuditService(BaseService[Audit, AuditCreate, AuditUpdate]):
    """Audit service."""
    dao = audit_dao
