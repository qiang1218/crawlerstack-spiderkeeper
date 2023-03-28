"""test project"""
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_server.models import Artifact
from crawlerstack_spiderkeeper_server.repository.project import \
    ProjectRepository
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist


@pytest.fixture()
async def repo():
    """repo fixture"""
    return ProjectRepository()


@pytest.mark.parametrize(
    'artifact_id, exist',
    [
        (1, True),
        (3, False)
    ]
)
async def test_get_project_from_artifact_id(init_artifact, repo, session, artifact_id, exist):
    """Test get a object."""
    if exist:
        exist_obj = await session.scalar(
            select(Artifact).filter(Artifact.id == artifact_id).options(selectinload(Artifact.project)))
        obj = await repo.get_project_from_artifact_id(exist_obj.id)
        assert obj
        assert exist_obj.project.id == obj.id
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.get_project_from_artifact_id(artifact_id)
