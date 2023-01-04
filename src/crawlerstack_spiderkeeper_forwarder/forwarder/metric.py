"""metric"""

from crawlerstack_spiderkeeper_forwarder.forwarder.base import BaseTask


class MetricPublishTask(BaseTask):
    """Metric publish task"""
    NAME = 'metric'
