"""project"""
from typing import List, Optional

from crawlerstack_spiderkeeper_server.messages.base import Message, Messages
from crawlerstack_spiderkeeper_server.schemas.project import ProjectSchema


class ProjectMessage(Message):
    """Project message"""
    data: Optional[ProjectSchema]


class ProjectMessages(Messages):
    """Project messages"""
    data: List[Optional[ProjectSchema]]
