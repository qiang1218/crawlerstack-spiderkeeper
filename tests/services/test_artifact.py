"""
Test artifact service.
"""
import os

import pytest
from fastapi import HTTPException, UploadFile

from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.services import artifact_file_service
from crawlerstack_spiderkeeper.utils import ArtifactMetadata


class TestArtifactFileService:
    """Test artifact file service."""

    @pytest.mark.asyncio
    async def test_create(self, init_project, session, demo_zip):
        """Test create artifact."""
        obj: Project = session.query(Project).first()
        filename = await artifact_file_service.create(project_id=obj.id, file=UploadFile(demo_zip))
        file_metadata = ArtifactMetadata(filename)
        assert os.path.exists(file_metadata.file)

    @pytest.mark.asyncio
    async def test_delete(self, artifact_metadata):
        """Test delete artifact file"""
        await artifact_file_service.delete(artifact_metadata.filename)

    @pytest.mark.asyncio
    async def test_delete_error(self):
        """Test raise Exception when delete artifact file."""
        with pytest.raises(HTTPException):
            await artifact_file_service.delete('/foo')
