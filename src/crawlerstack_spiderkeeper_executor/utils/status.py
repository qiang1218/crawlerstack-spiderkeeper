"""status"""
from enum import IntEnum


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
