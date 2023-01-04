"""collector"""
from crawlerstack_spiderkeeper_server.collectior.metric import MetricBackgroundTask
from crawlerstack_spiderkeeper_server.collectior.log import LogBackgroundTask
from crawlerstack_spiderkeeper_server.collectior.data import DataBackgroundTask
from crawlerstack_spiderkeeper_server.collectior.utils import Kombu
from crawlerstack_spiderkeeper_server.signals import server_start, server_stop

# 注册事件
server_start.connect(MetricBackgroundTask().start)
server_stop.connect(MetricBackgroundTask().stop)

server_start.connect(LogBackgroundTask().start)
server_stop.connect(LogBackgroundTask().stop)

server_start.connect(DataBackgroundTask().start)
server_stop.connect(DataBackgroundTask().stop)

server_start.connect(Kombu().server_start)
server_stop.connect(Kombu().server_stop)
