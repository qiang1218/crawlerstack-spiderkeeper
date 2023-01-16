"""forwarder"""
from crawlerstack_spiderkeeper_forwarder.forwarder.data import DataPublishTask
from crawlerstack_spiderkeeper_forwarder.forwarder.log import LogPublishTask
from crawlerstack_spiderkeeper_forwarder.forwarder.metric import \
    MetricPublishTask
from crawlerstack_spiderkeeper_server.signals import server_stop

# 注册事件
server_stop.connect(MetricPublishTask.stop_from_cls)

server_stop.connect(LogPublishTask.stop_from_cls)

server_stop.connect(DataPublishTask.stop_from_cls)
