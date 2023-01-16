"""Metric"""
from crawlerstack_spiderkeeper_forwarder.forwarder.metric import \
    MetricPublishTask
from crawlerstack_spiderkeeper_forwarder.services.base import EntityService


class MetricService(EntityService):
    """Metric service"""
    FORWARDER_CLASS = MetricPublishTask
