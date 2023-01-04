"""task"""
from typing import List, Optional

from crawlerstack_spiderkeeper_server.messages.base import Message, Messages
from crawlerstack_spiderkeeper_server.schemas.task import TaskSchema


class TaskMessage(Message):
    """Task message"""
    data: Optional[TaskSchema]


class TaskMessages(Messages):
    """Task messages"""
    data: List[Optional[TaskSchema]]
