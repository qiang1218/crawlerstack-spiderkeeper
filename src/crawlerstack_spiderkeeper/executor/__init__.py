"""
Executor API
"""
from typing import Type

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.executor.base import BaseExecutor
from crawlerstack_spiderkeeper.executor.docker import DockerExecutor
from crawlerstack_spiderkeeper.executor.local import LocalExecutor
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError


def executor_factory() -> Type[BaseExecutor]:
    """
    Executor factory.
    Create executor from settings.EXECUTOR
    :return:
    """
    executor = str(settings.EXECUTOR).lower()
    if executor == 'local':
        executor_kls = LocalExecutor
    elif executor == 'docker':
        executor_kls = DockerExecutor
    else:
        raise SpiderkeeperError('Invalid executor.')

    return executor_kls


__all__ = [
    'DockerExecutor',
    'LocalExecutor',
    'executor_factory'
]
