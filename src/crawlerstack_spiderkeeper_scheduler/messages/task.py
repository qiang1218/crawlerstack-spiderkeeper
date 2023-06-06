"""Task"""
from typing import List, Optional

from crawlerstack_spiderkeeper_scheduler.messages.base import Message, Messages
from crawlerstack_spiderkeeper_scheduler.schemas.task import (TaskCount,
                                                              TaskSchema)


class TaskMessage(Message):
    """Task message"""
    data: Optional[TaskSchema]


class TaskMessages(Messages):
    """Task messages"""
    data: List[Optional[TaskSchema]]


class TaskCountMessage(Message):
    """Task count message"""
    data: Optional[TaskCount]
