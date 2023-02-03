"""
Executor API
"""
from typing import Type

from crawlerstack_spiderkeeper_executor.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper_executor.config import settings
from crawlerstack_spiderkeeper_executor.executor.base import BaseExecutor
from crawlerstack_spiderkeeper_executor.executor.docker import DockerExecutor
from crawlerstack_spiderkeeper_executor.executor.k8s import K8SExecutor


def executor_factory() -> Type[BaseExecutor]:
    """
    Executor factory.
    Create executor from settings.EXECUTOR
    :return:
    """
    executor = str(settings.EXECUTOR_TYPE).lower()
    if executor == 'docker':
        executor_kls = DockerExecutor
    elif executor == 'k8s':
        executor_kls = K8SExecutor
    else:
        raise SpiderkeeperError('Invalid executor.')

    return executor_kls


__all__ = [
    'DockerExecutor',
    'executor_factory',
    'BaseExecutor',
    'K8SExecutor',
]
