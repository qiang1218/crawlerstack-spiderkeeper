"""status"""
from enum import Enum, IntEnum


# noinspection PyArgumentList
class Status(IntEnum):
    """
    Status enum
    """
    CREATED = 1
    RESTARTING = 2
    RUNNING = 3
    PAUSED = 4
    EXITED = 5
    DEAD = 6

    ONLINE = 7
    OFFLINE = 8

    FINISH = 0

    STOPPED = -1
    FAILURE = -2


# noinspection PyArgumentList
# pylint: disable=invalid-name
class ContainerStatus(Enum):
    """Container Status enum"""
    # docker 中 status=(created restarting running paused exited dead)，后续添加对k8s状态的支持映射
    created = 'CREATED'
    restarting = 'RESTARTING'
    running = 'RUNNING'
    paused = 'PAUSED'
    exited = 'EXITED'
    dead = 'DEAD'
