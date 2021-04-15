"""
Storate dao.
"""
from typing import List

from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db import ScopedSession as Session
from crawlerstack_spiderkeeper.db.models import Storage
from crawlerstack_spiderkeeper.schemas.storage import (StorageCreate,
                                                       StorageUpdate)
from crawlerstack_spiderkeeper.utils import scoping_session
from crawlerstack_spiderkeeper.utils.states import States

# pylint: disable=no-member


class StorageDAO(BaseDAO[Storage, StorageCreate, StorageUpdate]):
    """
    Storage dao.
    """

    @scoping_session
    def increase_storage_count_by_id(self, pk: int) -> Storage:
        """
        Increase storage count by count.
        :param pk:
        :return:
        """
        obj = self._get(pk)
        obj.count += 1
        Session.add(obj)
        Session.commit()
        Session.refresh(obj)
        return obj

    @scoping_session
    def running_storage(self) -> List[Storage]:  # pylint: disable=no-self-use
        """
        Run storage task.
        :return:
        """
        return Session.query(Storage).filter(Storage.state == States.Running.value).all()
