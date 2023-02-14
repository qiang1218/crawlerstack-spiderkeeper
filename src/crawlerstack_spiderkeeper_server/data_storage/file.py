"""file"""

from typing import Any

from crawlerstack_spiderkeeper_server.data_storage.base import Storage


class FileStorage(Storage):
    """file storage"""
    name: str = 'file'

    def save(self, *args, **kwargs) -> Any:
        """save"""
        raise NotImplementedError

    def start(self, *args, **kwargs) -> Any:
        """start"""
        raise NotImplementedError

    def clear(self, *args, **kwargs) -> Any:
        """close"""
        raise NotImplementedError

    async def expired(self, *args, **kwargs) -> Any:
        """expired"""
        raise NotImplementedError

    def stop(self, *args, **kwargs) -> Any:
        """stop"""
        raise NotImplementedError
