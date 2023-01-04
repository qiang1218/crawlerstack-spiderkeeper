"""data storage"""
import asyncio

from crawlerstack_spiderkeeper_server.data_storage.base import Storage
from crawlerstack_spiderkeeper_server.data_storage.mysql import MysqlStorage
from crawlerstack_spiderkeeper_server.data_storage.mongo import MongoStorage
from crawlerstack_spiderkeeper_server.data_storage.file import FileStorage

from crawlerstack_spiderkeeper_server.signals import server_start, server_stop


class StorageFactory:
    """
    保存工厂
    """
    storage_classes = [MysqlStorage, MongoStorage, FileStorage]
    storage_mapping = {i.name: i for i in storage_classes}

    def get_storage(self, storage_class: str, name: str, url: str) -> Storage:
        storage_kls = self.storage_mapping.get(storage_class)
        return storage_kls().start(name=name, url=url)


async def expired_task(**_):
    await asyncio.to_thread(MysqlStorage().expired)


server_start.connect(expired_task)
server_stop.connect(MysqlStorage().stop)

server_start.connect(MysqlStorage().server_start)
server_stop.connect(MysqlStorage().server_stop)
