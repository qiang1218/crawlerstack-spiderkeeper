"""
Jbo dao.
"""
from typing import Optional

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db import ScopedSession as Session
from crawlerstack_spiderkeeper.db.models import Job, Task
from crawlerstack_spiderkeeper.schemas.job import JobCreate, JobUpdate
from crawlerstack_spiderkeeper.utils import scoping_session
from crawlerstack_spiderkeeper.utils.states import States

# pylint: disable=no-member


class JobDAO(BaseDAO[Job, JobCreate, JobUpdate]):
    """
    Job dao.
    """

    @scoping_session
    def state(self, *, pk: int) -> Optional[States]:    # pylint: disable=no-self-use
        """
        Job state.
        :param pk:
        :return:
        """
        obj: Task = Session.query(Task).filter(Task.job_id == pk).order_by(Task.id.desc()).first()
        if obj:
            return States(obj.state)
        return None
