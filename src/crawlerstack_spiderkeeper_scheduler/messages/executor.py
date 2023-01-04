"""Executor"""
from typing import List, Optional

from crawlerstack_spiderkeeper_scheduler.messages.base import Message, Messages
from crawlerstack_spiderkeeper_scheduler.schemas.executor import ExecutorSchema


class ExecutorMessage(Message):
    """Executor message"""
    data: Optional[ExecutorSchema]


class ExecutorMessages(Messages):
    """Executor messages"""
    data: List[Optional[ExecutorSchema]]
