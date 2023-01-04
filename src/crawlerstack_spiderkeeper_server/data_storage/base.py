"""base"""
import dataclasses
from typing import Any

from datetime import datetime

from crawlerstack_spiderkeeper_server.utils import SingletonMeta


class Storage(metaclass=SingletonMeta):
    name: str

    _server_running = None

    @property
    def server_running(self) -> bool:
        return self._server_running

    def server_start(self, **_):
        if self._server_running is None:
            self._server_running = True

    def server_stop(self, **_):
        self._server_running = False

    def save(self, *args, **kwargs) -> Any:
        """save"""
        raise NotImplementedError

    def start(self, *args, **kwargs) -> Any:
        """connector"""
        raise NotImplementedError

    def clear(self, *args, **kwargs) -> Any:
        """close"""
        raise NotImplementedError

    def expired(self, *args, **kwargs) -> Any:
        """expired"""
        raise NotImplementedError

    def stop(self, *args, **kwargs) -> Any:
        """stop"""
        raise NotImplementedError


@dataclasses.dataclass
class Connector:
    name: str
    url: str
    expire_date: datetime
    conn: Any
