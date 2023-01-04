"""
Data schema
"""
from typing import Any

from pydantic import (BaseModel, constr)  # pylint: disable=no-name-in-module


class DataSchema(BaseModel):
    """Data schema."""
    task_name: constr(max_length=200)
    fields: list
    title: constr(max_length=200)
    data: list[tuple[Any]]

