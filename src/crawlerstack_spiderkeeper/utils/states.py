"""
1   Creat
2   Prepare
3   Start
4   Run
-1  Stop
0   Finish

"""
from enum import IntEnum


class States(IntEnum):
    """
    State enum
    """
    CREATED = 1
    BUILDING = 2
    PENDING = 3
    STARTED = 4
    RUNNING = 5

    FINISH = 0

    STOPPED = -1
    FAILURE = -2
