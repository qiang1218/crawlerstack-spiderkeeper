"""collector"""
from crawlerstack_spiderkeeper_server.collector.data import DataBackgroundTask
from crawlerstack_spiderkeeper_server.collector.log import LogBackgroundTask
from crawlerstack_spiderkeeper_server.collector.metric import \
    MetricBackgroundTask
from crawlerstack_spiderkeeper_server.collector.utils import Kombu
from crawlerstack_spiderkeeper_server.signals import (kombu_start, kombu_stop,
                                                      server_start,
                                                      server_stop)

__metric_bg_task = MetricBackgroundTask()
__log_bg_task = LogBackgroundTask()
__data_bg_task = DataBackgroundTask()

# 注册事件
server_start.connect(Kombu().server_start)
server_stop.connect(Kombu().server_stop)

kombu_start.connect(__metric_bg_task.start)
kombu_stop.connect(__metric_bg_task.stop)

kombu_start.connect(__log_bg_task.start)
kombu_stop.connect(__log_bg_task.stop)

kombu_start.connect(__data_bg_task.start)
kombu_stop.connect(__data_bg_task.stop)
