"""job"""
from typing import List, Optional

from crawlerstack_spiderkeeper_server.messages.base import Message, Messages
from crawlerstack_spiderkeeper_server.schemas.job import JobSchema


class JobMessage(Message):
    """Job message"""
    data: Optional[JobSchema]


class JobMessages(Messages):
    """Job messages"""
    data: List[Optional[JobSchema]]
