"""metric"""
from typing import List, Optional, Any

from crawlerstack_spiderkeeper_server.messages.base import Message


class MetricMessage(Message):
    """Metric message"""
    data: Optional[dict[str, Any]]
