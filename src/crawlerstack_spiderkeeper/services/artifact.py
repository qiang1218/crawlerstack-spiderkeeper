"""
Artifact service
"""
import asyncio
import logging
import os
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.datastructures import UploadFile

from crawlerstack_spiderkeeper.dao import ArtifactDAO, ProjectDAO
from crawlerstack_spiderkeeper.db.models import Artifact
from crawlerstack_spiderkeeper.schemas.artifact import (ArtifactCreate,
                                                        ArtifactUpdate, ArtifactFileCreate)
from crawlerstack_spiderkeeper.services.base import EntityService
from crawlerstack_spiderkeeper.utils import run_in_executor, upload
from crawlerstack_spiderkeeper.utils.metadata import ArtifactMetadata


class ArtifactService(EntityService[Artifact, ArtifactCreate, ArtifactUpdate]):
    """
    Artifact service
    """
    DAO_CLASS = ArtifactDAO

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._artifact_dao = ArtifactDAO(self.session)
        self._project_dao = ProjectDAO(self.session)
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    async def create_file(
            self,
            project_id: int,
            file: UploadFile
    ) -> str:
        """
        Create artifact file
        :param project_id:
        :param file:    aiofile obj
        :return:    Uploaded filename
        """
        project = await self._project_dao.get_by_id(project_id)
        file_metadata = ArtifactMetadata.from_project(project.slug)
        self.logger.debug('Write artifact to %s.', file_metadata.file)
        return await upload(file, file_metadata)

    async def create(self, obj_in: ArtifactFileCreate):
        filename = await self.create_file(obj_in.project_id, obj_in.file)
        return await self.dao.create(
            obj_in=ArtifactCreate(
                project_id=obj_in.project_id,
                interpreter=obj_in.interpreter,
                execute_path=obj_in.execute_path,
                filename=filename,
            ))

    async def get_project_of_artifacts(self, project_id: int) -> List[Artifact]:
        """
        Get project of artifacts
        :param project_id:
        :return:
        """
        return await run_in_executor(self.dao.get_project_of_artifacts, project_id=project_id)


class ArtifactFileService(EntityService):
    """
    Artifact file service
    """
    DAO_CLASS = ArtifactDAO

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._artifact_dao = ArtifactDAO(self.session)
        self._project_dao = ProjectDAO(self.session)
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    @property
    def project_dao(self) -> ProjectDAO:
        return self._project_dao

    async def create_file(
            self,
            project_id: int,
            file: UploadFile
    ) -> str:
        """
        Create artifact file
        :param project_id:
        :param file:    aiofile obj
        :return:    Uploaded filename
        """
        project = await self.project_dao.get_by_id(project_id)
        file_metadata = ArtifactMetadata.from_project(project.slug)
        self.logger.debug('Write artifact to %s.', file_metadata.file)
        return await upload(file, file_metadata)

    async def delete_file(
            self,
            filename: str
    ) -> None:
        """
        Delete artifact file.
        :param filename:
        :return:
        """
        file_metadata = ArtifactMetadata(filename)
        try:
            await asyncio.get_running_loop().run_in_executor(None, os.remove, file_metadata.file)
        except FileNotFoundError as ex:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'No such file or directory: {filename}'
            ) from ex
