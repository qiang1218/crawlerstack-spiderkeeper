"""
Server service.
"""
from crawlerstack_spiderkeeper.dao import ServerDAO
from crawlerstack_spiderkeeper.schemas.server import (Server, ServerCreate,
                                                      ServerUpdate)
from crawlerstack_spiderkeeper.services.base import EntityService


class ServerService(EntityService[Server, ServerCreate, ServerUpdate]):
    """
    Server service
    """
    DAO_CLASS = ServerDAO
