"""
Storage dao.
"""
from typing import List, Optional

from sqlalchemy import select

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db.models import Storage
from crawlerstack_spiderkeeper.schemas.storage import (StorageCreate,
                                                       StorageUpdate)
from crawlerstack_spiderkeeper.utils.exceptions import ObjectDoesNotExist
from crawlerstack_spiderkeeper.utils.status import Status


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

    async def running_storage(self) -> list[Storage]:
        """
        Run storage task.
        :return:
        """
        stmt = select(self.model).filter(self.model.status == Status.RUNNING.value)
        result = await self.session.execute(stmt)
        objs = result.scalars().all()
        if objs:
            return objs
        raise ObjectDoesNotExist()

    async def get_by_job_id(self, job_id: int) -> Storage:
        """使用 job id 获取 storage """
        obj = await self.session.scalar(
            select(self.model).filter(self.model.job_id == job_id)
        )
        if not obj:
            raise ObjectDoesNotExist()
        return obj
