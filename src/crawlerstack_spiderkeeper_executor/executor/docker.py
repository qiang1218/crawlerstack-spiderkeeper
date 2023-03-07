"""
Docker executor.
"""
import logging
from typing import Any

from aiodocker import Docker

from crawlerstack_spiderkeeper_executor.executor.base import BaseExecutor
from crawlerstack_spiderkeeper_executor.schemas.base import (ExecutorSchema,
                                                             SpiderSchema,
                                                             TaskSchema)

logger = logging.getLogger(__name__)


class DockerExecutor(BaseExecutor):
    """Docker executor"""
    NAME = 'docker'

    def __init__(self, settings):
        super().__init__(settings)
        self.client = Docker(url=self.settings.EXECUTOR_REMOTE_URL)
        self._prefix = 'SpiderKeeper-'

    async def get(self) -> list:
        """
        get all containers about spiderkeeper
        :return:
        """
        status = ["running", "paused", "exited", "dead"]
        containers = await self.client.containers.list(filters={'status': status, 'label': ["task_name"]})
        datas = []
        for i in containers:
            _container = i._container  # pylint: disable=W0212  # noqa
            container_id = _container.get('Id')[:12]
            status = _container.get('State')
            task_name = _container.get('Labels').get('task_name')
            datas.append(dict(container_id=container_id, status=status, task_name=task_name))

        return datas

    async def run(self, obj_in: TaskSchema, **_) -> str:
        """
        Run
        :param obj_in:
        :return:
        """
        # 1 参数拆分
        executor_params = obj_in.executor_params
        spider_params = obj_in.spider_params
        # 2 执行器的参数组装
        config = self._merge_executor_params(executor_params, spider_params)
        container_name = f'{self._prefix}{spider_params.TASK_NAME}'

        # 3 执行运行命令，包含镜像的 pull, create, start
        container = await self.client.containers.run(config=config, name=container_name)
        # 默认取12位值
        return container.id[:12]

    def _merge_executor_params(self, executor_params: ExecutorSchema, spider_params: SpiderSchema) -> dict[str, Any]:
        """
        Merge executor params
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
                  'Cmd': cmd,
                  'Env': environment,
                  'AttachStdin': False,
                  'AttachStdout': False,
                  'AttachStderr': False,
                  'Tty': False,
                  'OpenStdin': False,
                  'Detach': True,
                  'Labels': {'task_name': spider_params.TASK_NAME},
                  'HostConfig': {
                      'NetworkMode': self.settings.DOCKER_NETWORK,
                      'Init': True,
                      'Binds': executor_params.volume,
                      'AutoRemove': False},
                  'NetworkingConfig': {self.settings.Docker_NETWORK: None}
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

    async def stop(self, container_id: str, **_) -> str:
        """
        Stop
        :param container_id:
        :return:
        """
        logger.debug('Start stop a container: %s', container_id)
        await self.client.containers.container(container_id=container_id).stop()
        logger.debug('Stop a container: %s success.', container_id)
        return 'stop successful'

    async def delete(self, container_id: str, **_) -> str:
        """
        Delete
        :param container_id:
        :return:
        """
        logger.debug('Start delete a container: %s', container_id)
        await self.client.containers.container(container_id=container_id).delete()
        logger.debug('Delete a container: %s success.', container_id)
        return 'delete successful'

    async def status(self, container_id: str, **_) -> str:
        """
        Status
        已知的 status:
        - running
        - exited
        :param container_id:
        :return:
        """
        data = await self.client.containers.container(container_id=container_id).show()
        logger.debug('Inspect docker container: %s, response: %s', container_id, data)
        return data.get('State', {}).get('Status')

    async def log(self, container_id: str, follow=False, **_):
        """
        Log
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
    def format_command(command: str | list[str], step=' ') -> list[str] | str:
        """
        Retrieve command(s).
        """
        if isinstance(command, str) and command:
            return str.split(step)
        return command

    async def close(self):
        """Close"""
        await self.client.close()
