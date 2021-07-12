"""
Project dao
"""
from uuid import uuid4

from fastapi.encoders import jsonable_encoder

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.schemas.project import ProjectCreate
from crawlerstack_spiderkeeper.db import ScopedSession


class ProjectDAO(BaseDAO):
    """
    Project dao
    """
    model = Project

    async def create(self, *, obj_in: ProjectCreate) -> Project:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data.update({'slug': str(uuid4())})
        db_obj = self.model(**obj_in_data)
        ScopedSession.add(db_obj)
        return db_obj
