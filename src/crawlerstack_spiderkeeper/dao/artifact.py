"""
Artifact dao
"""
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db.models import Artifact, Job
from crawlerstack_spiderkeeper.schemas.artifact import (ArtifactCreate,
                                                        ArtifactUpdate)
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist


class ArtifactDAO(BaseDAO[Artifact, ArtifactCreate, ArtifactUpdate]):
    """Artifact dao"""
    model = Artifact

    async def get_project_of_artifacts(self, project_id: int) -> List[Artifact]:
        """
        Get project of artifacts
        :param project_id:
        :return:
        """
        stmt = select(self.model).filter(self.model.project_id == project_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_artifact_from_job_id(self, job_id: int) -> List[Artifact]:
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
        return job.artifact
