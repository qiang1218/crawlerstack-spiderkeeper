"""
Artifact dao
"""
from typing import List

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db import ScopedSession as Session
from crawlerstack_spiderkeeper.db.models import Artifact, Job
from crawlerstack_spiderkeeper.schemas.artifact import (ArtifactCreate,
                                                        ArtifactUpdate)
from crawlerstack_spiderkeeper.utils import scoping_session
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist


class ArtifactDAO(BaseDAO[Artifact, ArtifactCreate, ArtifactUpdate]):
    """Artifact dao"""

    @scoping_session
    def get_project_of_artifacts(self, project_id: int) -> List[Artifact]:
        """
        Get project of artifacts
        :param project_id:
        :return:
        """
        return Session.query(self.model).filter(self.model.project_id == project_id).all()

    @scoping_session
    def get_artifact_from_job_id(self, job_id: int) -> List[Artifact]:  # pylint: disable=no-self-use
        """
        Get artifact from job id
        :param job_id:
        :return:
        """
        job: Job = Session.query(Job).get(job_id)
        if not job:
            # Job does not exist
            raise ObjectDoesNotExist()
        return job.artifact
