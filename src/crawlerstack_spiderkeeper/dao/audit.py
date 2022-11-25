"""
Audit DAO
"""
from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db.models import Audit


class AuditDAO(BaseDAO):
    """
    Audit DAO.
    """
    model = Audit
