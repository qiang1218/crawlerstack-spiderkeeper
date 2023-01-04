"""Log"""
from crawlerstack_spiderkeeper_forwarder.services.base import EntityService

from crawlerstack_spiderkeeper_forwarder.forwarder.log import LogPublishTask


class LogService(EntityService):
    """Log service"""
    FORWARDER_CLASS = LogPublishTask
