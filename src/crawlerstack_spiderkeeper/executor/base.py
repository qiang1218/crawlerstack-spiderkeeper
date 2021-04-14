"""
Base executor.
"""
import asyncio
import logging
import os
from asyncio import AbstractEventLoop
from shutil import unpack_archive
from typing import Dict, List, Optional

from crawlerstack_spiderkeeper.utils import ArtifactMetadata

logger = logging.getLogger(__name__)


class BaseExecuteContext:
    """
    Base executor context.
    """

    def __init__(
            self,
            artifact: ArtifactMetadata,
            loop: Optional[AbstractEventLoop] = None
    ):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.loop = loop or asyncio.get_running_loop()
        self.artifact = artifact

    async def build(self) -> None:
        """
        Build executor context.
        :return:
        """
        raise NotImplementedError

    async def delete(self) -> None:
        """
        Delete executor context
        :return:
        """
        raise NotImplementedError

    async def exist(self) -> bool:
        """
        Check if context is exist.
        :return:
        """
        raise NotImplementedError

    async def unpack_artifact(self):
        """
        Unpack artifact.
        :return:
        """
        if not os.path.exists(self.artifact.source_code):
            artifact_file = self.artifact.file
            await self.loop.run_in_executor(
                None,
                unpack_archive,
                artifact_file,
                self.artifact.source_code
            )
            self.logger.debug(
                'Unpack artifact %s to %s',
                self.artifact.filename,
                self.artifact.source_code
            )
        else:
            self.logger.debug('%s exist, not unpack artifact.', self.artifact.source_code)

    async def close(self):
        """
        关闭某些操作，如果没有可以不用实现
        :return:
        """


class BaseExecutor:
    """
    Base executor.
    """
    _executor_context_cls = BaseExecuteContext

    def __init__(
            self,
            artifact: ArtifactMetadata,
            pid: str,
            loop: Optional[AbstractEventLoop] = None
    ):
        """
        :param artifact:
        :param pid:
        :param loop:
        """
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.artifact = artifact
        self.loop: AbstractEventLoop = loop or asyncio.get_running_loop()

        self.context = self._executor_context_cls(artifact, self.loop)

        self._pid = pid

    @property
    def pid(self) -> str:
        """
        Executor process id.
        :return:
        """
        return self._pid

    @classmethod
    def executor_context(cls, artifact: ArtifactMetadata) -> BaseExecuteContext:
        """
        Create executor with context.
        :param artifact:
        :return:
        """
        return cls._executor_context_cls(artifact)

    @classmethod
    async def run(
            cls,
            artifact: ArtifactMetadata,
            cmdline: List[str],
            env: Dict[str, str],
            target: Optional[str] = None,
            loop: Optional[AbstractEventLoop] = None
    ) -> 'BaseExecutor':
        """
        Run a executor.
        :param artifact:
        :param cmdline:
        :param env:
        :param target:
        :param loop:
        :return:
        """
        raise NotImplementedError

    async def stop(self):
        """
        Stop executor.
        :return:
        """
        raise NotImplementedError

    async def delete(self):
        """
        Delete executor.
        :return:
        """
        raise NotImplementedError

    async def running(self):
        """
        Check if executor is running.
        :return:
        """
        raise NotImplementedError

    async def status(self) -> str:
        """
        Get executor status.
        :return:
        """
        raise NotImplementedError

    async def log(self, follow=False):
        """
        Get executor log.
        :return:
        """
        raise NotImplementedError
