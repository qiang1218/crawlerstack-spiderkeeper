"""
Signals.
"""
from aio_pydispatch import Signal

server_start = Signal('server_start')

server_stop = Signal('server_stop')

job_start = Signal('job_start')
job_stop = Signal('job_stop')
