"""
Signals.
"""
from aio_pydispatch import Signal

server_start = Signal()
server_stop = Signal()

task_manual_trigger = Signal()
