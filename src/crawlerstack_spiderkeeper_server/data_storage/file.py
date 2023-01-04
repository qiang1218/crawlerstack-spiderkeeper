"""file"""

from typing import Any

from crawlerstack_spiderkeeper_server.data_storage.base import Storage


class FileStorage(Storage):
    name: str = 'file'

    async def save(self, *args, **kwargs) -> Any:
        """save"""
        pass

    async def start(self, *args, **kwargs) -> Any:
        """conn"""
        pass

    async def clear(self, *args, **kwargs) -> Any:
        """close"""
        raise NotImplementedError

    async def expired(self, *args, **kwargs) -> Any:
        """expired"""
        raise NotImplementedError

    def stop(self, *args, **kwargs) -> Any:
        """stop"""
        raise NotImplementedError
