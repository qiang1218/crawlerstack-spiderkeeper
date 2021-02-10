import asyncio
import logging
import os
from asyncio import AbstractEventLoop
from shutil import unpack_archive
from typing import Dict, List, Optional

from crawlerstack_spiderkeeper.utils import ArtifactMetadata

logger = logging.getLogger(__name__)


class BaseExecuteContext:

    def __init__(
            self,
            artifact: ArtifactMetadata,
            loop: Optional[AbstractEventLoop] = None
    ):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.loop = loop or asyncio.get_running_loop()
        self.artifact = artifact

    async def build(self) -> None:
        raise NotImplementedError

    async def delete(self) -> None:
        raise NotImplementedError

    async def exist(self) -> bool:
        raise NotImplementedError

    async def unpack_artifact(self):
        if not os.path.exists(self.artifact.source_code):
            artifact_file = self.artifact.file
            await self.loop.run_in_executor(
                None,
                unpack_archive,
                artifact_file,
                self.artifact.source_code
            )
            self.logger.debug(f'Unpack artifact {self.artifact.filename} to {self.artifact.source_code}')
        else:
            self.logger.debug(f'{self.artifact.source_code} exist, not unpack artifact.')

    async def close(self):
        """
        关闭某些操作，如果没有可以不用实现
        :return:
        """
        pass


class BaseExecutor:
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
        return self._pid

    @classmethod
    def executor_context(cls, artifact: ArtifactMetadata) -> BaseExecuteContext:
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
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError

    async def delete(self):
        raise NotImplementedError

    async def running(self):
        raise NotImplementedError

    async def status(self) -> str:
        raise NotImplementedError

    async def log(self):
        raise NotImplementedError
