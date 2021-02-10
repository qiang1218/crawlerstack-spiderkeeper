import asyncio
import logging
import os
from typing import List

from fastapi import HTTPException
from starlette import status
from starlette.datastructures import UploadFile

from crawlerstack_spiderkeeper.dao import artifact_dao, project_dao
from crawlerstack_spiderkeeper.db.models import Artifact
from crawlerstack_spiderkeeper.schemas.artifact import (ArtifactCreate,
                                                        ArtifactUpdate)
from crawlerstack_spiderkeeper.services.base import BaseService
from crawlerstack_spiderkeeper.utils import run_in_executor, upload
from crawlerstack_spiderkeeper.utils.metadata import ArtifactMetadata


class ArtifactService(BaseService[Artifact, ArtifactCreate, ArtifactUpdate]):
    dao = artifact_dao

    async def get_project_of_artifacts(self, project_id: int) -> List[Artifact]:
        return await run_in_executor(self.dao.get_project_of_artifacts, project_id=project_id)


class ArtifactFileService:

    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    async def create(
            self,
            project_id: int,
            file: UploadFile
    ) -> str:
        """

        :param session:
        :param project_id:
        :param file:    aiofile obj
        :return:    Uploaded filename
        """
        project = await run_in_executor(project_dao.get, pk=project_id)
        file_metadata = ArtifactMetadata.from_project(project.slug)
        self.logger.debug(f'Write artifact to {file_metadata.file}.')
        return await upload(file, file_metadata)

    async def delete(
            self,
            filename: str
    ) -> None:
        file_metadata = ArtifactMetadata(filename)
        try:
            await asyncio.get_running_loop().run_in_executor(None, os.remove, file_metadata.file)
        except FileNotFoundError as e:
            self.logger.error(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No such file or directory: {filename}')
