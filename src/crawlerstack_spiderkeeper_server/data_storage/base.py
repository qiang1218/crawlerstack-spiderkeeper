"""Base"""
import dataclasses
import logging
from datetime import datetime
from typing import Any

from crawlerstack_spiderkeeper_server.utils import SingletonMeta

logger = logging.getLogger(__name__)


class Storage(metaclass=SingletonMeta):
    """Storage"""
    name: str

    _server_running = None

    @property
    def server_running(self) -> bool:
        """Server running"""
        return self._server_running

    async def server_start(self, **_):
        """Server start"""
        if self._server_running is None:
            logger.debug('Change %s.server_running to "True"', self.__class__.name)
            self._server_running = True

    async def server_stop(self, **_):
        """Server stop"""
        logger.debug('Change %s.server_running to "False"', self.__class__.name)
        self._server_running = False

    def save(self, *args, **kwargs) -> Any:
        """Save"""
        raise NotImplementedError

    def start(self, *args, **kwargs) -> Any:
        """Connector"""
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


@dataclasses.dataclass
class Connector:
    """Connector"""
    name: str
    url: str
    expire_date: datetime
    conn: Any
