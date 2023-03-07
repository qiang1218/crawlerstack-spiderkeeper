"""Storage server"""
from crawlerstack_spiderkeeper_server.models import StorageServer
from crawlerstack_spiderkeeper_server.repository.storage_server import \
    StorageServerRepository
from crawlerstack_spiderkeeper_server.schemas.storage_server import (
    StorageServerCreate, StorageServerSchema, StorageServerUpdate)
from crawlerstack_spiderkeeper_server.services.base import EntityService


class StorageServerService(EntityService[StorageServer, StorageServerCreate, StorageServerUpdate, StorageServerSchema]):
    """
    Storage server service.
    """
    REPOSITORY_CLASS = StorageServerRepository

    async def get_storage_server_from_job_id(self, job_id: int) -> StorageServerSchema:
        """
        Get storage server from job id
        :param job_id:
        :return:
        """
        return await self.repository.get_storage_server_from_job_id(job_id)

    async def get_snapshot_server_from_job_id(self, job_id: int) -> StorageServerSchema:
        """
        Get snapshot server form job id
        :param job_id:
        :return:
        """
        return await self.repository.get_snapshot_server_from_job_id(job_id)
