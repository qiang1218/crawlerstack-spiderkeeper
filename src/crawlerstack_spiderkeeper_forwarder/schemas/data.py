"""
Data schema
"""
from typing import Any

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module


class DataContentSchema(BaseModel):
    """Data content schema"""
    title: constr(max_length=200)
    fields: list
    datas: list[tuple[Any] | list[Any]]


class DataSchema(BaseModel):
    """Data schema."""
    task_name: constr(max_length=200)
    data: DataContentSchema
