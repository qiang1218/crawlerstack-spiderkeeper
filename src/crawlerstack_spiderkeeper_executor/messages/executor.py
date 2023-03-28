"""executor"""

from pydantic import BaseModel

from crawlerstack_spiderkeeper_executor.messages.base import Message


class ExecutorMixin(BaseModel):
    """Mixin executor"""
    container_id: str
    status: str


class ExecutorMessage(Message):
    """Executor message"""
    data: ExecutorMixin


class ExecutorAllMixin(ExecutorMixin):
    """Mixin all executor"""
    task_name: str


class ExecutorAllMessage(Message):
    """Executor message"""
    data: list[ExecutorAllMixin]
