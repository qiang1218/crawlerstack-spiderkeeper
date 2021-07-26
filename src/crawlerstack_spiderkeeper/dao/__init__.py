"""
Data access object interface.
"""
from crawlerstack_spiderkeeper.dao.artifact import ArtifactDAO
from crawlerstack_spiderkeeper.dao.audit import AuditDAO
from crawlerstack_spiderkeeper.dao.job import JobDAO
from crawlerstack_spiderkeeper.dao.project import ProjectDAO
from crawlerstack_spiderkeeper.dao.server import ServerDAO
from crawlerstack_spiderkeeper.dao.storage import StorageDAO
from crawlerstack_spiderkeeper.dao.task import TaskDAO

__all__ = [
    'ArtifactDAO',
    'AuditDAO',
    'JobDAO',
    'ProjectDAO',
    'ServerDAO',
    'StorageDAO',
    'TaskDAO',
]
