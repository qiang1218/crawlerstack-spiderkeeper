"""
Test artifact service.
"""
import os

import pytest
from fastapi import HTTPException, UploadFile
from sqlalchemy import select

from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.services import ArtifactFileService
from crawlerstack_spiderkeeper.utils import ArtifactMetadata


class TestArtifactFileService:
    """Test artifact file service."""

    @pytest.mark.asyncio
    async def test_create(self, init_project, session, demo_zip, factory_with_session):
        """Test create artifact."""
        obj: Project = await session.scalar(select(Project))
        async with factory_with_session(ArtifactFileService) as service:

            filename = await service.create_file(project_id=obj.id, file=UploadFile(demo_zip))
            file_metadata = ArtifactMetadata(filename)
            assert os.path.exists(file_metadata.file)

    @pytest.mark.asyncio
    async def test_delete(self, artifact_metadata, factory_with_session):
        """Test delete artifact file"""
        async with factory_with_session(ArtifactFileService) as service:
            await service.delete_file(artifact_metadata.filename)

    @pytest.mark.asyncio
    async def test_delete_error(self, factory_with_session):
        """Test raise Exception when delete artifact file."""
        async with factory_with_session(ArtifactFileService) as service:
            with pytest.raises(HTTPException):
                await service.delete_file('/foo')
