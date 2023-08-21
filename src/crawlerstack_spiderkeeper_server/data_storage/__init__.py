"""data storage"""

from crawlerstack_spiderkeeper_server.data_storage.base import Storage
from crawlerstack_spiderkeeper_server.data_storage.mongo import MongoStorage
from crawlerstack_spiderkeeper_server.data_storage.mysql import MysqlStorage
from crawlerstack_spiderkeeper_server.data_storage.pulsar import PulsarStorage
from crawlerstack_spiderkeeper_server.data_storage.s3_file import FileStorage
from crawlerstack_spiderkeeper_server.signals import server_start, server_stop


class StorageFactory:
    """
    保存工厂
    """
    storage_classes = [MysqlStorage, MongoStorage, FileStorage, PulsarStorage]
    storage_mapping = {i.name: i for i in storage_classes}

    def get_storage(self, storage_class: str, name: str, url: str) -> Storage:
        """get storage"""
        storage_kls = self.storage_mapping.get(storage_class)
        return storage_kls().start(name=name, url=url)


server_start.connect(MysqlStorage().server_start)
server_stop.connect(MysqlStorage().server_stop)

server_start.connect(MysqlStorage().expired)
server_stop.connect(MysqlStorage().stop)

server_start.connect(MongoStorage().server_start)
server_stop.connect(MongoStorage().server_stop)

server_start.connect(MongoStorage().expired)
server_stop.connect(MongoStorage().stop)

server_start.connect(FileStorage().server_start)
server_stop.connect(FileStorage().server_stop)

server_start.connect(FileStorage().expired)
server_stop.connect(FileStorage().stop)

server_start.connect(FileStorage().archive)
