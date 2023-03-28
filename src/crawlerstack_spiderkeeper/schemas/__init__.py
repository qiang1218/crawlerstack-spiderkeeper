"""
Schema
"""
from typing import Dict, Literal

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class AppData(BaseModel):  # pylint: disable=too-few-public-methods
    """AppData schema"""
    app_id: str
    data: Dict


class ActionResult(BaseModel):
    """
    Action 操作格式
    """
    success: bool
    message: str


class StatusResult(BaseModel):
    """
    状态结果格式
    """
    status: Literal['CREATED', 'BUILDING', 'PENDING',
                    'STARTED', 'RUNNING', 'FINISH',
                    'STOPPED', 'FAILURE']
