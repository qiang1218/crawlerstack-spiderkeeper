"""Data"""
from crawlerstack_spiderkeeper_forwarder.services.base import EntityService

from crawlerstack_spiderkeeper_forwarder.forwarder.data import DataPublishTask


class DataService(EntityService):
    """Data service"""
    FORWARDER_CLASS = DataPublishTask
