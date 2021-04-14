"""
Project dao
"""
from uuid import uuid4

from fastapi.encoders import jsonable_encoder

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db import ScopedSession as Session
from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.schemas.project import ProjectCreate
from crawlerstack_spiderkeeper.utils import scoping_session


# pylint: disable=no-member

class ProjectDAO(BaseDAO):
    """
    Project dao
    """
    @scoping_session
    def create(self, *, obj_in: ProjectCreate) -> Project:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data.update({'slug': str(uuid4())})
        db_obj = self.model(**obj_in_data)  # type: ignore
        Session.add(db_obj)
        Session.commit()
        Session.refresh(db_obj)
        return db_obj
