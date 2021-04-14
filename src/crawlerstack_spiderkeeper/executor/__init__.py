"""
Executor API
"""
from typing import Type

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.executor.base import BaseExecutor
from crawlerstack_spiderkeeper.executor.docker import DockerExecutor
from crawlerstack_spiderkeeper.executor.local import LocalExecutor


def executor_factory() -> Type[BaseExecutor]:
    """
    Executor factory.
    Create executor from settings.EXECUTOR
    :return:
    """
    executor = str(settings.EXECUTOR).lower()
    # pylint: disable=no-else-return
    if executor == 'local':
        return LocalExecutor
    elif executor == 'docker':
        return DockerExecutor
    else:
        raise Exception('Executor invalid.')
