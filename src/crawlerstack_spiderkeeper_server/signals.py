"""
Signals.
"""
from aio_pydispatch import Signal

server_start = Signal()
server_stop = Signal()

kombu_start = Signal()
kombu_stop = Signal()
