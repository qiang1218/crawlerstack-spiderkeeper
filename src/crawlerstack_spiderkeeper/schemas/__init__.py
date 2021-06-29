"""
Schema
"""
from typing import Dict

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class AppData(BaseModel):   # pylint: disable=too-few-public-methods
    """AppData schema"""
    app_id: str
    data: Dict
