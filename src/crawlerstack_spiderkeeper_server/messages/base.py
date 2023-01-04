"""base"""

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class BaseMessage(BaseModel):
    """Base Message"""
    message: str = 'ok'


class Message(BaseMessage):
    """Message"""


class Messages(BaseMessage):
    """Messages"""
    total_count: int = 0
    page: int = 0
    size: int = 0
