"""
Docker executor.
"""
import json
import logging
import os
from asyncio.events import AbstractEventLoop
from contextlib import asynccontextmanager
from shutil import make_archive
from tempfile import TemporaryDirectory
from typing import AsyncIterable, Dict, List, Optional

from aiodocker import Docker, DockerError
from aiodocker.containers import DockerContainer

from crawlerstack_spiderkeeper import signals
from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.executor.base import (BaseExecuteContext,
                                                     BaseExecutor)
from crawlerstack_spiderkeeper.utils import ArtifactMetadata, staging_path

logger = logging.getLogger(__name__)


class SingletonDocker(Docker):
    """
    Docker singleton.
    """
    __instance = None

    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            signals.server_stop.connect(cls.__instance.close)
        return cls.__instance

    async def close(self) -> None:
        """
        将 close 绑定到 server_stop 事件上，在事件触发时，先移除此单利对象然后停止 Docker 的连接。
        :return:
        """
        self.__instance = None
        await super().close()


class DocketExecuteContext(BaseExecuteContext):
    """
    Docker execute context.
    """

    def __init__(
            self,
            artifact: ArtifactMetadata,
            loop: Optional[AbstractEventLoop] = None,
    ):
        super().__init__(artifact, loop)

        self.client = SingletonDocker(settings.DOCKER_URL)

    @asynccontextmanager
    async def _make_docker_tar(self) -> str:
        """
        请使用上下文操作。
        从源码构建的 docket tar 文件放在临时目录中，如果不使用上下文，临时文件引用消失就会自动清理，导致后续无法读取该文件，
        :return:
        """
        await self.unpack_artifact()
        tmp_path = TemporaryDirectory(
            prefix=f'spiderkeeper-docker-build-{self.artifact.project_name}'
        )
        basename, _ = self.artifact.filename.rsplit('.', 1)
        with staging_path(tmp_path.name):
            await self.loop.run_in_executor(
                None,
                make_archive,
                basename,
                'gztar',
                self.artifact.source_code
            )
        yield os.path.join(tmp_path.name, f'{basename}.tar.gz')
        tmp_path.cleanup()

    async def build(self) -> None:
        """
        https://docs.docker.com/engine/api/v1.40/#operation/ImageBuild
        :return: image tag
        """
        async with self._make_docker_tar() as file:
            with open(file, 'rb') as file_obj:
                self.logger.debug('Start build docker image from %s', file)
                response = await self.client.images.build(
                    fileobj=file_obj,
                    tag=self.artifact.image_tag,
                    encoding='gzip',
                    rm=True,
                    nocache=True
                )
        last_response = response[-1]
        if last_response.get('stream') and 'Successfully' in last_response.get('stream'):
            self.logger.debug('Build docker image : %s success.', self.artifact.image_tag)
        else:  # Build error
            raise Exception(last_response.get('errorDetail') or last_response)

    async def delete(self) -> None:
        """
        # https://docs.docker.com/engine/api/v1.40/#operation/ImageDelete
        status: 200
            [{"Untagged": "3e2f21a89f"},
             {"Deleted": "53b4f83ac9"}]
        status: 404
            {"message": "Something went wrong."}
        status: 409
            {"message": "Something went wrong."}
        status: 409
            {"message": "Something went wrong."}

        删除 Docker 镜像。
        如果操作成功，返回状态码为 200 后面的内容。有时候可能没有 {"Deleted": "53b4f83ac9"}。
            这是因为该镜像有的父镜像存在。如果仅有该镜像则会出现删除信息。
        如果失败则抛出 DockerError 异常，异常有上面几种情况。
        :return:
        """
        try:
            self.logger.debug('Start delete docker image: %s', self.artifact.image_tag)
            await self.client.images.delete(self.artifact.image_tag)
            self.logger.debug('Delete docker image: %s success.', self.artifact.image_tag)
        except DockerError as ex:
            if ex.status == 404:
                logger.warning(
                    'Docker image: %s not found, skip. %s',
                    self.artifact.image_tag,
                    ex.message
                )
            else:
                raise ex

    async def exist(self) -> bool:
        """
        https://docs.docker.com/engine/api/v1.40/#operation/ImageCreate
        :return:
        """
        try:
            await self.client.images.inspect(self.artifact.image_tag)
            self.logger.debug('Docker image: %s exist.', self.artifact.image_tag)
            return True
        except DockerError as ex:
            if ex.status == 404:
                self.logger.debug('Docker image: %s does not exist.', self.artifact.image_tag)
                return False
            raise ex


class DockerExecutor(BaseExecutor):
    """
    Docker executor.
    """
    _executor_context_cls = DocketExecuteContext

    def __init__(
            self,
            artifact: ArtifactMetadata,
            pid: str,
            loop: Optional[AbstractEventLoop] = None
    ):
        super().__init__(artifact, pid, loop)

        self.client = SingletonDocker(settings.DOCKER_URL)

        self._container: Optional[DockerContainer] = None

    @classmethod
    async def run(
            cls,
            artifact: ArtifactMetadata,
            cmdline: List[str],
            env: Dict[str, str],
            target: Optional[str] = None,
            loop: Optional[AbstractEventLoop] = None
    ) -> 'DockerExecutor':
        """
        https://docs.docker.com/engine/api/v1.40/#operation/ContainerCreate
        :param artifact:
        :param cmdline: 'python print("hello world")'
        :param env: ["test=1", "xxx=abc"]
        :param target:
        :param loop:
        :return:
        """

        executor_context = cls._executor_context_cls(artifact, loop)
        if not await executor_context.exist():
            await executor_context.build()

        client = SingletonDocker(settings.DOCKER_URL)
        env.update({
            'SPIDERKEEPER_HOST_ADDR': settings.HOST_ADDR,
        })
        envs = cls._convert_env(env)

        config = {
            "Cmd": cmdline,
            "Image": artifact.image_tag,
            "AttachStdin": False,
            "AttachStdout": False,
            "AttachStderr": False,
            "Tty": False,
            "OpenStdin": False,
            'Env': envs,
            'HostConfig': {
                'NetworkMode': settings.DOCKER_NETWORK,
                'Init': True
            },
            'NetworkingConfig': {settings.DOCKER_NETWORK: None},
        }
        _logger = logging.getLogger(f'{__name__}.{cls.__name__}')
        _logger.debug('Start create container. data: %s', json.dumps(config))
        container = await client.containers.run(config, name=None)
        _logger.debug('Docker container: %s create success.', container.id)
        obj = cls(artifact, str(container.id), loop)
        return obj

    @property
    async def container(self) -> DockerContainer:
        """
        Docker container.
        :return:
        """
        if self._container is None:
            self._container = await self.client.containers.get(self.pid)
            self.logger.debug('Get container from container id: %s success.', self.pid)
        return self._container

    @staticmethod
    def _convert_env(env: Dict[str, str]) -> Optional[List[str]]:
        """
        Convert env to pass docker.
        :param env:
        :return:
        """
        envs = []
        for key, value in env.items():
            envs.append(f'{key}={value}')
        return envs

    async def stop(self) -> None:
        """
        Stop a docker container.
        :return:
        """
        container = await self.container
        self.logger.debug('Start stop a container: %s', container.id)
        await container.stop()
        self.logger.debug('Stop a container: %s success.', container.id)

    async def delete(self):
        """
        Delete docker
        :return:
        """
        await self.stop()
        container = await self.container
        self.logger.debug('Start delete a container: %s', container.id)
        await container.delete()
        self.logger.debug('Delete a container: %s success.', container.id)

    async def running(self) -> bool:
        """
        https://docs.docker.com/engine/api/v1.40/#operation/ContainerInspect
        响应示例请参考 docs/aiodocker.md
        已知的 status:
        - running
        - exited
        :return:
        """
        container = await self.container
        data = await container.show()
        self.logger.debug('Inspect docker container: %s, response: %s', container.id, data)
        running = data['State']['Running']
        if running:
            return True
        return False

    async def status(self) -> Dict:
        """
        Docker container status.
        :return:
        """
        container = await self.container
        data = await container.show()
        self.logger.debug('Inspect docker container: %s, response: %s', container.id, data)
        return {
            'state': data['State']['Status'],
            'detail': data
        }

    async def log(self, follow=False) -> AsyncIterable[str]:
        """
        Docker container log.
        :param follow:
        :return:
        """
        container: DockerContainer = await self.container
        if follow:
            async for line in container.log(stderr=True, stdout=True, follow=follow, tail=50):
                yield line
        else:
            res = await container.log(stderr=True, stdout=True, follow=follow, tail=50)
            for line in res:
                yield line
