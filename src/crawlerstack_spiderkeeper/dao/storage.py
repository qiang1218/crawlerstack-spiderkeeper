"""
Storage dao.
"""
from typing import List, Optional

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

    async def get_by_job_id(self, job_id: int) -> Optional[Storage]:
        """使用 job id 获取 storage """
        return await self.session.scalar(
            select(self.model).filter(self.model.job_id == job_id)
        )
