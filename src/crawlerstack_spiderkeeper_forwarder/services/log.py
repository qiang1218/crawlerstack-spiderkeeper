"""Log"""
from crawlerstack_spiderkeeper_forwarder.forwarder.log import LogPublishTask
from crawlerstack_spiderkeeper_forwarder.services.base import EntityService


class LogService(EntityService):
    """Log service"""
    FORWARDER_CLASS = LogPublishTask
