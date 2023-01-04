"""storage server"""
from typing import List, Optional

from crawlerstack_spiderkeeper_server.messages.base import Message, Messages
from crawlerstack_spiderkeeper_server.schemas.storage_server import StorageServerSchema


class StorageServerMessage(Message):
    """Project message"""
    data: Optional[StorageServerSchema]


class StorageServerMessages(Messages):
    """Project messages"""
    data: List[Optional[StorageServerSchema]]
