from typing import Type

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.executor.base import BaseExecutor
from crawlerstack_spiderkeeper.executor.docker import DockerExecutor
from crawlerstack_spiderkeeper.executor.local import LocalExecutor


def executor_factory() -> Type[BaseExecutor]:
    executor = str(settings.EXECUTOR).lower()
    if executor == 'local':
        return LocalExecutor
    elif executor == 'docker':
        return DockerExecutor
