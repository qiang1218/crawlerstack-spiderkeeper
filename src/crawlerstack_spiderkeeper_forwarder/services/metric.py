"""Metric"""
from crawlerstack_spiderkeeper_forwarder.services.base import EntityService

from crawlerstack_spiderkeeper_forwarder.forwarder.metric import MetricPublishTask


class MetricService(EntityService):
    """Metric service"""
    FORWARDER_CLASS = MetricPublishTask
