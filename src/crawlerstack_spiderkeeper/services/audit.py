"""
Audit service.
"""


from crawlerstack_spiderkeeper.dao import AuditDAO
from crawlerstack_spiderkeeper.schemas.audit import (Audit, AuditCreate,
                                                     AuditUpdate)
from crawlerstack_spiderkeeper.services.base import EntityService


class AuditService(EntityService[Audit, AuditCreate, AuditUpdate]):
    """Audit service."""
    DAO_CLASS = AuditDAO
