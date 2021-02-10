from crawlerstack_spiderkeeper.dao.artifact import ArtifactDAO
from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.dao.job import JobDAO
from crawlerstack_spiderkeeper.dao.project import ProjectDAO
from crawlerstack_spiderkeeper.dao.server import ServerDAO
from crawlerstack_spiderkeeper.dao.storage import StorageDAO
from crawlerstack_spiderkeeper.dao.task import TaskDAO
from crawlerstack_spiderkeeper.db.models import (Artifact, Audit, Job, Project,
                                                 Server, Storage, Task)

project_dao = ProjectDAO(Project)
artifact_dao = ArtifactDAO(Artifact)
job_dao = JobDAO(Job)
task_dao = TaskDAO(Task)
storage_dao = StorageDAO(Storage)
server_dao = ServerDAO(Server)
audit_dao = BaseDAO(Audit)

__all__ = [
    project_dao,
    artifact_dao,
    job_dao,
    task_dao,
    storage_dao,
    server_dao,
    audit_dao,
]
