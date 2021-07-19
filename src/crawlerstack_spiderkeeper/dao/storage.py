"""
Storage dao.
"""
from typing import List

from sqlalchemy import select

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db.models import Storage
from crawlerstack_spiderkeeper.schemas.storage import (StorageCreate,
                                                       StorageUpdate)
from crawlerstack_spiderkeeper.utils.states import States


class StorageDAO(BaseDAO[Storage, StorageCreate, StorageUpdate]):
    """
    Storage dao.
    """
    model = Storage

    async def increase_storage_count(self, pk: int) -> Storage:
        """
        Increase storage count by count.
        :param pk:
        :return:
        """
        obj = await self.get_by_id(pk)
        obj.count += 1
        return obj

    async def running_storage(self) -> List[Storage]:
        """
        Run storage task.
        :return:
        """
        stmt = select(self.model).filter(self.model.state == States.RUNNING.value)
        result = await self.session.execute(stmt)
        return result.scalars().all()
