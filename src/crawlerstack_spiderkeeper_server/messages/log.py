"""log"""
from typing import List, Optional

from crawlerstack_spiderkeeper_server.messages.base import Message


class LogMessage(Message):
    """Log message"""
    data: Optional[List[str]]
