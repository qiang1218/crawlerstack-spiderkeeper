"""
Server service.
"""
from crawlerstack_spiderkeeper.dao import server_dao
from crawlerstack_spiderkeeper.schemas.server import (Server, ServerCreate,
                                                      ServerUpdate)
from crawlerstack_spiderkeeper.services.base import BaseService


class ServerService(BaseService[Server, ServerCreate, ServerUpdate]):
    """
    Server service
    """
    dao = server_dao
