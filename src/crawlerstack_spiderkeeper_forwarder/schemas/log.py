"""
Log schema
"""
from pydantic import (BaseModel, constr)  # pylint: disable=no-name-in-module


class LogSchema(BaseModel):
    """Data schema."""
    task_name: constr(max_length=200)
    data: list[str] | tuple[str]
