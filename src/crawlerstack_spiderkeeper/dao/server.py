"""
Server dao.
"""
from typing import Optional

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db import ScopedSession as Session
from crawlerstack_spiderkeeper.db.models import Job, Server
from crawlerstack_spiderkeeper.schemas.server import ServerCreate, ServerUpdate
from crawlerstack_spiderkeeper.utils import scoping_session

# pylint: disable=no-member


class ServerDAO(BaseDAO[Server, ServerCreate, ServerUpdate]):
    """
    Server dao.
    """
    @scoping_session
    def get_server_by_job_id(self, job_id: int) -> Optional[Server]:    # pylint: disable=no-self-use
        """
        Get server by job id.
        :param job_id:
        :return:
        """
        job: Job = Session.query(Job).get(job_id)
        return job.server
