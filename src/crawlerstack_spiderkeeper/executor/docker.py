import json
import logging
import os
import tempfile
from asyncio.events import AbstractEventLoop
from contextlib import asynccontextmanager
from shutil import make_archive
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
    __instance = None

    def __new__(cls, *args, **kwargs):
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
        tmp_path = tempfile.TemporaryDirectory(prefix=f'spiderkeeper-docker-build-{self.artifact.project_name}')
        basename, fmt = self.artifact.filename.rsplit('.', 1)
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
        status: 200
            Because of `stream = False`, so it is build stdout.
            The image tag in last output.
            [
                {
                    "stream": "Step 1/1 : FROM python"
                },
                {
                    "stream": "\n"
                },
                {
                    "stream": " ---> 0a3a95c81a2b\n"
                },
                {
                    "aux": {
                        "ID": "sha256:0a3a95c81a2bd8d2ee9653097a4e0ae63d8765636874083afb5e9a7d52b6b9f1"
                    }
                },
                {
                    "stream": "Successfully built 0a3a95c81a2b\n"
                },
                {
                    "stream": "Successfully tagged p_01:20191226113941\n"
                }
            ]
            Or building error, the last one is not `stream`
             {'errorDetail': {'code': 1, 'message': "The command '/bi......"}}
        status: 404
            {
                "message": "Something went wrong."
            }
        status: 500
            {
                "message": "Something went wrong."
            }
        :return: image tag
        """
        async with self._make_docker_tar() as file:
            with open(file, 'rb') as file_obj:
                self.logger.debug(f'Start build docker image from {file}')
                response = await self.client.images.build(
                    fileobj=file_obj,
                    tag=self.artifact.image_tag,
                    encoding='gzip',
                    rm=True,
                    nocache=True
                )
        last_response = response[-1]
        if last_response.get('stream') and 'Successfully' in last_response.get('stream'):
            self.logger.debug(f'Build docker image : {self.artifact.image_tag} success.')
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
            self.logger.debug(f'Start delete docker image: {self.artifact.image_tag}')
            await self.client.images.delete(self.artifact.image_tag)
            self.logger.debug(f'Delete docker image: {self.artifact.image_tag} success.')
        except DockerError as e:
            if e.status == 404:
                logger.warning(f'Docker image: {self.artifact.image_tag} not found, skip. {e.message}')
            else:
                raise e

    async def exist(self) -> bool:
        """
        https://docs.docker.com/engine/api/v1.40/#operation/ImageCreate
        status 200 :
            {
                "Id": "sha256:85f05633ddc1c50679be2b16a0479ab6f7637f8884e0cfe0f4d20e1ebb3d6e7c",
                "Container": "cb91e48a60d01f1e27028b4fc6819f4f290b3cf12496c8176ec714d0d390984a",
                "Comment": "",
                "Os": "linux",
                "Architecture": "amd64",
                "Parent": "sha256:91e54dfb11794fad694460162bf0cb0a4fa710cfa3f60979c177d920813e267c",
                "ContainerConfig": {
                    "Tty": false,
                    "Hostname": "e611e15f9c9d",
                    "Domainname": "",
                    "AttachStdout": false,
                    "PublishService": "",
                    "AttachStdin": false,
                    "OpenStdin": false,
                    "StdinOnce": false,
                    "NetworkDisabled": false,
                    "OnBuild": [],
                    "Image": "91e54dfb11794fad694460162bf0cb0a4fa710cfa3f60979c177d920813e267c",
                    "User": "",
                    "WorkingDir": "",
                    "MacAddress": "",
                    "AttachStderr": false,
                    "Labels": {
                        "com.example.license": "GPL",
                        "com.example.version": "1.0",
                        "com.example.vendor": "Acme"
                    },
                    "Env": [
                        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                    ],
                    "Cmd": [
                        "/bin/sh",
                        "-c",
                        "#(nop) LABEL com.example.vendor=Acme com.example.license=GPL com.example.version=1.0"
                    ]
                },
                "DockerVersion": "1.9.0-dev",
                "VirtualSize": 188359297,
                "Size": 0,
                "Author": "",
                "Created": "2015-09-10T08:30:53.26995814Z",
                "GraphDriver": {
                    "Name": "aufs",
                    "Data": {}
                },
                "RepoDigests": [
                    "localhost:5000/test/busybox/example@sha256:cbbf2f9a99b47fc460d422812b6a5adff7dfee951d8fa2e4a98caa0382cfbdbf"
                ],
                "RepoTags": [
                    "example:1.0",
                    "example:latest",
                    "example:stable"
                ],
                "Config": {
                    "Image": "91e54dfb11794fad694460162bf0cb0a4fa710cfa3f60979c177d920813e267c",
                    "NetworkDisabled": false,
                    "OnBuild": [],
                    "StdinOnce": false,
                    "PublishService": "",
                    "AttachStdin": false,
                    "OpenStdin": false,
                    "Domainname": "",
                    "AttachStdout": false,
                    "Tty": false,
                    "Hostname": "e611e15f9c9d",
                    "Cmd": [
                        "/bin/bash"
                    ],
                    "Env": [
                        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                    ],
                    "Labels": {
                        "com.example.vendor": "Acme",
                        "com.example.version": "1.0",
                        "com.example.license": "GPL"
                    },
                    "MacAddress": "",
                    "AttachStderr": false,
                    "WorkingDir": "",
                    "User": ""
                },
                "RootFS": {
                    "Type": "layers",
                    "Layers": [
                        "sha256:1834950e52ce4d5a88a1bbd131c537f4d0e56d10ff0dd69e66be3b7dfa9df7e6",
                        "sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef"
                    ]
                }
            }

        status 404:
        {
            "message": "No such image: someimage (tag: latest)"
        }

        stat8s 500:
        {
            "message": "Something went wrong."
        }
        :return:
        """
        try:
            await self.client.images.inspect(self.artifact.image_tag)
            self.logger.debug(f'Docker image: {self.artifact.image_tag} exist.')
            return True
        except DockerError as e:
            if e.status == 404:
                self.logger.debug(f'Docker image: {self.artifact.image_tag} does not exist.')
                return False
            raise e


class DockerExecutor(BaseExecutor):
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
        _logger.debug(f'Start create container. data: {json.dumps(config)}')
        container = await client.containers.run(config, name=None)
        _logger.debug(f'Docker container: {container.id} create success.')
        obj = cls(artifact, str(container.id), loop)
        obj._container = container
        return obj

    @property
    async def container(self) -> DockerContainer:
        if self._container is None:
            self._container = await self.client.containers.get(self.pid)
            self.logger.debug(f'Get container from container id: {self.pid} success.')
        return self._container

    @staticmethod
    def _convert_env(env: Dict[str, str]) -> Optional[List[str]]:
        envs = []
        for k, v in env.items():
            envs.append(f'{k}={v}')
        return envs

    async def stop(self) -> None:
        container = await self.container
        self.logger.debug(f'Start stop a container: {container.id}')
        await container.stop()
        self.logger.debug(f'Stop a container: {container.id} success.')

    async def delete(self):
        await self.stop()
        container = await self.container
        self.logger.debug(f'Start delete a container: {container.id}')
        await container.delete()
        self.logger.debug(f'Delete a container: {container.id} success.')

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
        self.logger.debug(f'Inspect docker container: {container.id}, response: {data}')
        running = data['State']['Running']
        if running:
            return True
        return False

    async def status(self) -> Dict:
        container = await self.container
        data = await container.show()
        self.logger.debug(f'Inspect docker container: {container.id}, response: {data}')
        return {
            'state': data['State']['Status'],
            'detail': data
        }

    async def log(self, follow=False) -> AsyncIterable[str]:
        container: DockerContainer = await self.container
        if follow:
            async for line in container.log(stderr=True, stdout=True, follow=follow, tail=50):
                yield line
        else:
            res = await container.log(stderr=True, stdout=True, follow=follow, tail=50)
            for line in res:
                yield line
