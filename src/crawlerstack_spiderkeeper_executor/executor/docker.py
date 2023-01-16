"""
Docker executor.
"""
import ast
import logging
from typing import Any

from aiodocker import Docker

from crawlerstack_spiderkeeper_executor.executor.base import BaseExecutor
from crawlerstack_spiderkeeper_executor.schemas.base import (ExecutorSchema,
                                                             SpiderSchema,
                                                             TaskSchema)

logger = logging.getLogger(__name__)


class DockerExecutor(BaseExecutor):
    NAME = 'docker'

    def __init__(self, settings):
        super(DockerExecutor, self).__init__(settings)
        self.client = Docker(url=self.settings.EXECUTOR_REMOTE_URL)

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
        # 默认取12位值
        return container.id[:12]

    def _merge_executor_params(self, executor_params: ExecutorSchema, spider_params: SpiderSchema) -> dict[str, Any]:
        """
        merge executor params
        :param executor_params:
        :param spider_params:
        :return:
        """
        image_name = executor_params.image
        cmd = executor_params.cmdline
        environment = executor_params.environment if executor_params.environment else []
        # 爬虫新加参数与页面传递的环境变量参数一起合并
        environment.extend(self._convert_env(spider_params.dict()))

        config = {'Image': image_name,
                  'Cmd': self.format_command(cmd),
                  'Env': environment,
                  'AttachStdin': False,
                  'AttachStdout': False,
                  'AttachStderr': False,
                  'Tty': False,
                  'OpenStdin': False,
                  "Detach": True,
                  'NetworkDisabled': True,
                  'HostConfig': {
                      'NetworkMode': self.settings.DOCKER_NETWORK,
                      'Init': True,
                      'Binds': executor_params.volume,
                      'AutoRemove': False
                  }}
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
        logger.debug('Start stop a container: %s', container_id)
        await self.client.containers.container(container_id=container_id).stop()
        logger.debug('Stop a container: %s success.', container_id)

    async def delete(self, container_id: str):
        """
        delete
        :param container_id:
        :return:
        """
        logger.debug('Start delete a container: %s', container_id)
        await self.client.containers.container(container_id=container_id).delete()
        logger.debug('Delete a container: %s success.', container_id)

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
        logger.debug('Inspect docker container: %s, response: %s', container_id, data)
        return data.get('State', {}).get('Status')

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

    async def close(self):
        """close"""
        await self.client.close()
