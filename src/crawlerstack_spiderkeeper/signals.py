"""
Signals.
"""
from aio_pydispatch import Signal

server_start = Signal()

server_stop = Signal()

job_start = Signal()
job_stop = Signal()
