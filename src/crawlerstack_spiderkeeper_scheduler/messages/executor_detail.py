"""Executor detail"""
from typing import List, Optional

from crawlerstack_spiderkeeper_scheduler.messages.base import Message, Messages
from crawlerstack_spiderkeeper_scheduler.schemas.executor_detail import ExecutorDetailSchema


class ExecutorDetailMessage(Message):
    """Executor detail message"""
    data: Optional[ExecutorDetailSchema]


class ExecutorDetailMessages(Messages):
    """Executor detail messages"""
    data: List[Optional[ExecutorDetailSchema]]
