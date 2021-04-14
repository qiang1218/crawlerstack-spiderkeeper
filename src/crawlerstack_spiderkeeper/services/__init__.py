"""
Service
"""
from crawlerstack_spiderkeeper.services.artifact import (ArtifactFileService,
                                                         ArtifactService)
from crawlerstack_spiderkeeper.services.audit import AuditService
from crawlerstack_spiderkeeper.services.base import ProjectService
from crawlerstack_spiderkeeper.services.job import JobService
from crawlerstack_spiderkeeper.services.metric import MetricService
from crawlerstack_spiderkeeper.services.server import ServerService
from crawlerstack_spiderkeeper.services.storage import StorageService
from crawlerstack_spiderkeeper.services.task import TaskService

project_service = ProjectService()
artifact_service = ArtifactService()
artifact_file_service = ArtifactFileService()
job_service = JobService()
task_service = TaskService()
storage_service = StorageService()
metric_service = MetricService()
server_service = ServerService()
audit_service = AuditService()
