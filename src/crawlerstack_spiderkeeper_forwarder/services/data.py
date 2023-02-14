"""Data"""
from crawlerstack_spiderkeeper_forwarder.forwarder.data import DataPublishTask
from crawlerstack_spiderkeeper_forwarder.services.base import EntityService


class DataService(EntityService):
    """Data service"""
    FORWARDER_CLASS = DataPublishTask
