"""task detail"""
from typing import List, Optional

from crawlerstack_spiderkeeper_server.messages.base import Message, Messages
from crawlerstack_spiderkeeper_server.schemas.task_detail import \
    TaskDetailSchema


class TaskDetailMessage(Message):
    """Task detail message"""
    data: Optional[TaskDetailSchema]


class TaskDetailMessages(Messages):
    """Task detail messages"""
    data: List[Optional[TaskDetailSchema]]
