"""Artifact"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from crawlerstack_spiderkeeper_server.repository.base import BaseRepository

from crawlerstack_spiderkeeper_server.models import Artifact, Job
from crawlerstack_spiderkeeper_server.schemas.artifact import (ArtifactCreate, ArtifactUpdate, ArtifactSchema)
from crawlerstack_spiderkeeper_server.utils.exceptions import ObjectDoesNotExist


class ArtifactRepository(BaseRepository[Artifact, ArtifactCreate, ArtifactUpdate, ArtifactSchema]):
    """
    artifact repository
    """
    model = Artifact
    model_schema = ArtifactSchema

    async def get_artifact_from_job_id(self, job_id: int) -> ArtifactSchema:
        """
        Get artifact from job id
        :param job_id:
        :return:
        """
        stmt = select(Job).filter(Job.id == job_id).options(selectinload(Job.artifact))
        job: Job = await self.session.scalar(stmt)
        if not job:
            # Job does not exist
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(job.artifact)
