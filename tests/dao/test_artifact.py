"""
Test artifact dao.
"""
import pytest

from crawlerstack_spiderkeeper.dao import artifact_dao
from crawlerstack_spiderkeeper.db.models import Job
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist


def test_get_artifact_from_job_id(init_job, session):
    """Test get artifact from job id."""
    jobs = session.query(Job).all()
    job = artifact_dao.get_artifact_from_job_id(jobs[0].id)
    assert job.id == jobs[0].id
    with pytest.raises(ObjectDoesNotExist):
        artifact_dao.get_artifact_from_job_id(len(jobs) + 1)
