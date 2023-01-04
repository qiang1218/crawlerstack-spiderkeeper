"""Storage server"""
from crawlerstack_spiderkeeper_server.services.base import EntityService
from crawlerstack_spiderkeeper_server.models import StorageServer
from crawlerstack_spiderkeeper_server.schemas.storage_server import StorageServerCreate, StorageServerUpdate, StorageServerSchema
from crawlerstack_spiderkeeper_server.repository.storage_server import StorageServerRepository


class StorageServerService(EntityService[StorageServer, StorageServerCreate, StorageServerUpdate, StorageServerSchema]):
    """
    Storage server service.
    """
    REPOSITORY_CLASS = StorageServerRepository
