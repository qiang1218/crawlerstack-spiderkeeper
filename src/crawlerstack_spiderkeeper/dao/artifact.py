from typing import List

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db import ScopedSession as Session
from crawlerstack_spiderkeeper.db.models import Artifact, Job
from crawlerstack_spiderkeeper.schemas.artifact import (ArtifactCreate,
                                                        ArtifactUpdate)
from crawlerstack_spiderkeeper.utils import scoping_session
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist


class ArtifactDAO(BaseDAO[Artifact, ArtifactCreate, ArtifactUpdate]):

    @scoping_session
    def get_project_of_artifacts(self, project_id: int) -> List[Artifact]:
        return Session.query(self.model).filter(self.model.project_id == project_id).all()

    @scoping_session
    def get_artifact_from_job_id(self, job_id: int) -> List[Artifact]:
        job: Job = Session.query(Job).get(job_id)
        if not job:
            # Job does not exist
            raise ObjectDoesNotExist()
        return job.artifact
