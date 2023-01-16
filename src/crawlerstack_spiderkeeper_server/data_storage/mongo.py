"""mongo"""

from typing import Any

from crawlerstack_spiderkeeper_server.data_storage.base import Storage


class MongoStorage(Storage):
    """Mongo storage"""
    name: str = 'mongo'

    def save(self, *args, **kwargs) -> Any:
        """Save"""
        raise NotImplementedError

    def start(self, *args, **kwargs) -> Any:
        """Start"""
        raise NotImplementedError

    def clear(self, *args, **kwargs) -> Any:
        """Close"""
        raise NotImplementedError

    async def expired(self, *args, **kwargs) -> Any:
        """Expired"""
        raise NotImplementedError

    def stop(self, *args, **kwargs) -> Any:
        """Stop"""
        raise NotImplementedError
