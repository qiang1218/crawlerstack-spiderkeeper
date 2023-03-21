"""
Base executor.
"""
import logging

from crawlerstack_spiderkeeper_executor.utils import SingletonMeta

logger = logging.getLogger(__name__)


class BaseExecutor(metaclass=SingletonMeta):
    """
    Base executor.
    """
    NAME: str

    def __init__(self, settings):
        self.settings = settings
        self._prefix = 'spiderkeeper-'

    async def get(self, *args, **kwargs):
        """
        Get
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def run(self, *args, **kwargs):
        """
        Run
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def stop(self, *args, **kwargs):
        """
        Stop
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def delete(self, *args, **kwargs):
        """
        Delete
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def status(self, *args, **kwargs) -> str:
        """
        Get container status.
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def log(self, *args, **kwargs):
        """
        Get container logs.
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def close(self, *args, **kwargs):
        """
        Close connection
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def resource(self, *args, **kwargs):
        """
        Get executor resource
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError