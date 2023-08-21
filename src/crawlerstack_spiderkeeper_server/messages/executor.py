"""Executor"""
from typing import List, Optional

from crawlerstack_spiderkeeper_server.messages.base import Messages
from crawlerstack_spiderkeeper_server.schemas.executor import ExecutorSchema


class ExecutorMessages(Messages):
    """Executor messages"""
    data: List[Optional[ExecutorSchema]]
