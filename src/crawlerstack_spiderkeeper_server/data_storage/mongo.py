"""mongo"""

from typing import Any

from crawlerstack_spiderkeeper_server.data_storage.base import Storage


class MongoStorage(Storage):
    name: str = 'mongo'

    def save(self, *args, **kwargs) -> Any:
        """save"""
        pass

    def start(self, *args, **kwargs) -> Any:
        """start"""
        pass

    def clear(self, *args, **kwargs) -> Any:
        """close"""
        raise NotImplementedError

    def expired(self, *args, **kwargs) -> Any:
        """expired"""
        raise NotImplementedError

    def stop(self, *args, **kwargs) -> Any:
        """stop"""
        raise NotImplementedError


