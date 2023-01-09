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
