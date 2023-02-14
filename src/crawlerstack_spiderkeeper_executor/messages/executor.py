"""executor"""

from pydantic import BaseModel

from crawlerstack_spiderkeeper_executor.messages.base import Message


class ExecutorMixin(BaseModel):
    """mixin Executor"""
    container_id: str
    status: str


class ExecutorMessage(Message):
    """Executor message"""
    data: ExecutorMixin
