"""forwarder"""
from crawlerstack_spiderkeeper_forwarder.forwarder.utils import Kombu
from crawlerstack_spiderkeeper_forwarder.signals import (server_start,
                                                         server_stop)

server_start.connect(Kombu().server_start)
server_stop.connect(Kombu().server_stop)
