"""
Server dao.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db.models import Job, Server
from crawlerstack_spiderkeeper.schemas.server import ServerCreate, ServerUpdate


class ServerDAO(BaseDAO[Server, ServerCreate, ServerUpdate]):
    """
    Server dao.
    """
    model = Server

    async def get_server_by_job_id(self, job_id: int) -> Optional[Server]:
        """
        Get server by job id.
        :param job_id:
        :return:
        """
        stmt = select(Job).filter(Job.id == job_id).options(selectinload(Job.server))
        job: Job = await self.session.scalar(stmt)
        return job.server
