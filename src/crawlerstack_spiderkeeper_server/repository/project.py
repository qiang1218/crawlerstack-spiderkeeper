"""project"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from crawlerstack_spiderkeeper_server.repository.base import BaseRepository

from crawlerstack_spiderkeeper_server.models import Project, Artifact
from crawlerstack_spiderkeeper_server.schemas.project import (ProjectCreate, ProjectUpdate, ProjectSchema)
from crawlerstack_spiderkeeper_server.utils.exceptions import ObjectDoesNotExist


class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate, ProjectSchema]):
    """
    project repository
    """
    model = Project
    model_schema = ProjectSchema

    async def get_project_from_artifact_id(self, artifact_id: int) -> ProjectSchema:
        """
        Get job from artifact id
        :param artifact_id:
        :return:
        """
        stmt = select(Artifact).filter(Artifact.id == artifact_id).options(selectinload(Artifact.project))
        artifact: Artifact = await self.session.scalar(stmt)
        if not artifact:
            # artifact does not exist
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(artifact.project)
