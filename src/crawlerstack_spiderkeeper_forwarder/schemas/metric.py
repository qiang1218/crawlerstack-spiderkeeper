"""
Metric schema
"""
from typing import Any

from pydantic import (BaseModel, constr)  # pylint: disable=no-name-in-module


class MetricSchema(BaseModel):
    """Metric schema."""
    task_name: constr(max_length=200)
    data: dict[str, Any]
