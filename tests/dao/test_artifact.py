"""
Test artifact dao.
"""
import pytest
from sqlalchemy import func, select

from crawlerstack_spiderkeeper.dao.artifact import ArtifactDAO
from crawlerstack_spiderkeeper.db.models import Artifact, Job, Project
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist


@pytest.fixture()
async def dao(dao_factory):
    async with dao_factory(ArtifactDAO) as _dao:
        yield _dao


@pytest.mark.asyncio
async def test_get_artifact_from_job_id(init_job, session, dao):
    """Test get artifact from job id."""
    result = await session.execute(select(Job))
    jobs = result.scalars().all()
    job = await dao.get_artifact_from_job_id(jobs[0].id)
    assert job.id == jobs[0].id
    with pytest.raises(ObjectDoesNotExist):
        await dao.get_artifact_from_job_id(len(jobs) + 1)


@pytest.mark.parametrize(
    'exist',
    [True, False]
)
@pytest.mark.asyncio
async def test_get_project_of_artifacts(init_project, init_artifact, session, dao, exist):
    """test get_project_of_artifacts"""
    if exist:
        project_obj = await session.scalar(select(Project))
        objs = await dao.get_project_of_artifacts(project_id=project_obj.id)
        stmt = select(func.count()).select_from(Artifact)
        assert len(objs) == await session.scalar(stmt)
    else:
        objs = await dao.get_project_of_artifacts(project_id=100)
        assert not objs
