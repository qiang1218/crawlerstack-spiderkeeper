"""Artifact"""
from typing import Any, Dict, Union

from crawlerstack_spiderkeeper_server.models import Artifact
from crawlerstack_spiderkeeper_server.repository.artifact import \
    ArtifactRepository
from crawlerstack_spiderkeeper_server.repository.project import \
    ProjectRepository
from crawlerstack_spiderkeeper_server.schemas.artifact import (ArtifactCreate,
                                                               ArtifactSchema,
                                                               ArtifactUpdate)
from crawlerstack_spiderkeeper_server.schemas.project import ProjectSchema
from crawlerstack_spiderkeeper_server.services.base import EntityService
from crawlerstack_spiderkeeper_server.utils.types import (CreateSchemaType,
                                                          ModelSchemaType,
                                                          UpdateSchemaType)


class ArtifactService(EntityService[Artifact, ArtifactCreate, ArtifactUpdate, ArtifactSchema]):
    """
    Project service.
    """
    REPOSITORY_CLASS = ArtifactRepository

    @property
    def project_repository(self):
        return ProjectRepository()

    async def create(
            self,
            *,
            obj_in: CreateSchemaType
    ) -> ModelSchemaType:
        """
        Create a record.
        :param obj_in:
        :return:
        """
        await self.project_repository.exists(obj_in.project_id)
        return await self.repository.create(obj_in=obj_in)

    async def update_by_id(
            self,
            pk: int,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelSchemaType:
        """
        Update a record.
        :param pk:
        :param obj_in:
        :return:
        """
        # 局部更新时
        project_id = obj_in.project_id
        if project_id is not None:
            await self.project_repository.exists(obj_in.project_id)
        return await self.repository.update_by_id(pk=pk, obj_in=obj_in)

    async def get_project_from_artifact_id(self, pk: int) -> ProjectSchema:
        """
        get a project from artifact id
        :param pk:
        :return:
        """
        return await self.project_repository.get_project_from_artifact_id(pk)
