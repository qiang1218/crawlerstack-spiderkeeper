from typing import List

from crawlerstack_spiderkeeper.dao import BaseDAO
from crawlerstack_spiderkeeper.db import ScopedSession as Session
from crawlerstack_spiderkeeper.db.models import Storage
from crawlerstack_spiderkeeper.schemas.storage import (StorageCreate,
                                                       StorageUpdate)
from crawlerstack_spiderkeeper.utils import scoping_session
from crawlerstack_spiderkeeper.utils.states import States


class StorageDAO(BaseDAO[Storage, StorageCreate, StorageUpdate]):

    @scoping_session
    def increase_storage_count_by_id(self, pk: int) -> Storage:
        obj = self._get(pk)
        obj.count += 1
        Session.add(obj)
        Session.commit()
        Session.refresh(obj)
        return obj

    @scoping_session
    def running_storage(self) -> List[Storage]:
        return Session.query(Storage).filter(Storage.state == States.Running.value).all()
