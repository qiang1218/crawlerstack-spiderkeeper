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
    Created = 1
    Building = 2
    Pending = 3
    Started = 4
    Running = 5

    Finish = 0

    Stopped = -1
    Failure = -2
