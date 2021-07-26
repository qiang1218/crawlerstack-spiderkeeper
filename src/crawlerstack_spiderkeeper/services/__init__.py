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

__all__ = [
    'ArtifactService',
    'ArtifactFileService',
    'AuditService',
    'ProjectService',
    'JobService',
    'MetricService',
    'ServerService',
    'StorageService',
    'TaskService'
]


# TODO 当所有测试完成后，移除这部分代码 !!!
# 这部分代码是在测试 Service 模块代码的时候，为 API 层代码做的补丁。
# 当 API 部分测试完成后，这部分代码需要移除掉。
audit_service = None
artifact_file_service = None
artifact_service = None
job_service = None
metric_service = None
project_service = None
server_service = None
storage_service = None
task_service = None
