"""
Test artifact dao.
"""
import pytest

from crawlerstack_spiderkeeper.dao import artifact_dao
from crawlerstack_spiderkeeper.db.models import Artifact, Job, Project
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist


def test_get_artifact_from_job_id(init_job, session):
    """Test get artifact from job id."""
    jobs = session.query(Job).all()
    job = artifact_dao.get_artifact_from_job_id(jobs[0].id)
    assert job.id == jobs[0].id
    with pytest.raises(ObjectDoesNotExist):
        artifact_dao.get_artifact_from_job_id(len(jobs) + 1)


@pytest.mark.parametrize(
    'exist',
    [True, False]
)
def test_get_project_of_artifacts(init_project, init_artifact, session, exist):
    """test get_project_of_artifacts"""
    if exist:
        project_obj = session.query(Project).first()
        objs = artifact_dao.get_project_of_artifacts(project_id=project_obj.id)
        assert len(objs) == session.query(Artifact).count()
    else:
        objs = artifact_dao.get_project_of_artifacts(project_id=100)
        assert not objs
