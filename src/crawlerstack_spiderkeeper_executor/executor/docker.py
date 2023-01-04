"""
Docker executor.
"""
import ast
import logging
from typing import Any

from aiodocker import Docker

from crawlerstack_spiderkeeper_executor.signals import server_stop
from crawlerstack_spiderkeeper_executor.config import settings
from crawlerstack_spiderkeeper_executor.executor.base import BaseExecutor

from crawlerstack_spiderkeeper_executor.schemas.base import TaskSchema, SpiderSchema, ExecutorSchema

logger = logging.getLogger(__name__)


class SingletonDocker(Docker):
    """
    Docker singleton.
    """
    __instance = None

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls)
            server_stop.connect(cls.__instance.close)
        return cls.__instance

    async def close(self) -> None:
        """
        将 close 绑定到 server_stop 事件上，在事件触发时，先移除此单利对象然后停止 Docker 的连接。
        :return:
        """
        self.__instance = None  # pylint: disable=unused-private-member
        await super().close()


class DockerExecutor(BaseExecutor):
    NAME = 'docker'

    def __init__(self, ):
        super().__init__()
        self.client = SingletonDocker(url=settings.EXECUTOR_REMOTE_URL)
        self.logger = logger

    async def run(self, obj_in: TaskSchema) -> str:
        """
        run
        :param obj_in:
        :return:
        """
        # 1 参数拆分
        executor_params = obj_in.executor_params
        spider_params = obj_in.spider_params
        # 2 执行器的参数组装
        config = self._merge_executor_params(executor_params, spider_params)
        container_name = f'SpiderKeeper-{spider_params.TASK_NAME}'

        # 3 执行运行命令，包含镜像的 pull, create, start
        container = await self.client.containers.run(config=config, name=container_name)
        return container.id

    def _merge_executor_params(self, executor_params: ExecutorSchema, spider_params: SpiderSchema) -> dict[str, Any]:
        """
        merge executor params
        :param executor_params:
        :param spider_params:
        :return:
        """
        image_name = executor_params.image
        cmd = executor_params.cmdline
        environment = executor_params.environment
        # 爬虫新加参数与页面传递的环境变量参数一起合并
        environment.append(self._convert_env(spider_params.dict()))

        config = {'Image': image_name,
                  'Cmd': self.format_command(cmd),
                  'Env': environment,
                  'AttachStdin': False,
                  'AttachStdout': False,
                  'AttachStderr': False,
                  'Tty': False,
                  'OpenStdin': False,
                  'HostConfig': {
                      'NetworkMode': settings.DOCKER_NETWORK,
                      'Init': True,
                      'Binds': executor_params.volume,
                      'AutoRemove': True
                  },
                  'NetworkingConfig': {settings.DOCKER_NETWORK: None},
                  }
        return config

    @staticmethod
    def _convert_env(env: dict[str, Any]) -> list[str]:
        """
        Convert env to pass docker.
        :param env:
        :return:
        """
        envs = []
        for key, value in env.items():
            envs.append(f'{key}={value}')
        return envs

    async def stop(self, container_id: str):
        """
        stop
        :param container_id:
        :return:
        """
        self.logger.debug('Start stop a container: %s', container_id)
        await self.client.containers.container(container_id=container_id).stop()
        self.logger.debug('Stop a container: %s success.', container_id)

    async def delete(self, container_id: str):
        """
        delete
        :param container_id:
        :return:
        """
        self.logger.debug('Start delete a container: %s', container_id)
        await self.client.containers.container(container_id=container_id).delete()
        self.logger.debug('Delete a container: %s success.', container_id)

    async def status(self, container_id: str):
        """
        status
        已知的 status:
        - running
        - exited
        :param container_id:
        :return:
        """
        data = await self.client.containers.container(container_id=container_id).show()
        self.logger.debug('Inspect docker container: %s, response: %s', container_id, data)
        return data['Status']

    async def log(self, container_id: str, follow=False):
        """
        log
        :param container_id:
        :param follow:
        :return:
        """
        container = self.client.containers.container(container_id=container_id)
        if follow:
            async for line in container.log(stderr=True, stdout=True, follow=follow, tail=50):
                yield line
        else:
            res = await container.log(stderr=True, stdout=True, follow=follow, tail=50)
            for line in res:
                yield line

    @staticmethod
    def format_command(command: str | list[str]) -> list[str] | str:
        """
        Retrieve command(s). if command string starts with [, it returns the command list)
        """
        if isinstance(command, str) and command.strip().find("[") == 0:
            return ast.literal_eval(command)
        return command
