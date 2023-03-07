"""collector"""
from crawlerstack_spiderkeeper_server.collector.data import DataBackgroundTask
from crawlerstack_spiderkeeper_server.collector.log import LogBackgroundTask
from crawlerstack_spiderkeeper_server.collector.metric import \
    MetricBackgroundTask
from crawlerstack_spiderkeeper_server.collector.utils import Kombu
from crawlerstack_spiderkeeper_server.signals import (data_task_clear,
                                                      data_task_start,
                                                      data_task_terminate,
                                                      kombu_start, kombu_stop,
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

data_task_start.connect(__data_bg_task.start)
data_task_clear.connect(__data_bg_task.clear)
data_task_terminate.connect(__data_bg_task.terminate)

kombu_start.connect(__data_bg_task.init_lift_cycle)

kombu_start.connect(__data_bg_task.server_start)
kombu_start.connect(__data_bg_task.update_life_cycle)
kombu_stop.connect(__data_bg_task.server_stop)
kombu_stop.connect(__data_bg_task.stop)
