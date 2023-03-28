"""artifact"""
from typing import List, Optional

from crawlerstack_spiderkeeper_server.messages.base import Message, Messages
from crawlerstack_spiderkeeper_server.schemas.artifact import ArtifactSchema


class ArtifactMessage(Message):
    """Artifact message"""
    data: Optional[ArtifactSchema]


class ArtifactMessages(Messages):
    """Artifact messages"""
    data: List[Optional[ArtifactSchema]]
