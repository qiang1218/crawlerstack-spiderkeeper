"""base"""
import dataclasses
import logging
from datetime import datetime
from typing import Any

from crawlerstack_spiderkeeper_server.utils import SingletonMeta

logger = logging.getLogger(__name__)


class Storage(metaclass=SingletonMeta):
    name: str

    _server_running = None

    @property
    def server_running(self) -> bool:
        return self._server_running

    async def server_start(self, **_):
        if self._server_running is None:
            logger.debug(f'Change {self.__class__.name}.server_running to "True"')
            self._server_running = True

    async def server_stop(self, **_):
        logger.debug(f'Change {self.__class__.name}.server_running to "False"')
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
