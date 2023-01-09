"""StorageServer repository"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from crawlerstack_spiderkeeper_server.repository.base import BaseRepository

from crawlerstack_spiderkeeper_server.models import StorageServer, Job
from crawlerstack_spiderkeeper_server.schemas.storage_server import (StorageServerCreate, StorageServerUpdate,
                                                                     StorageServerSchema)
from crawlerstack_spiderkeeper_server.utils.exceptions import ObjectDoesNotExist


class StorageServerRepository(BaseRepository[StorageServer, StorageServerCreate,
                                             StorageServerUpdate, StorageServerSchema]):
    """
    StorageServer repository
    """
    model = StorageServer
    model_schema = StorageServerSchema

    async def get_storage_server_from_job_id(self, job_id: int) -> StorageServerSchema:
        """
        Get storage server from job id
        :param job_id:
        :return:
        """
        stmt = select(Job).filter(Job.id == job_id).options(selectinload(Job.storage_server))
        job: Job = await self.session.scalar(stmt)
        if not job:
            # Job does not exist
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(job.storage_server)
