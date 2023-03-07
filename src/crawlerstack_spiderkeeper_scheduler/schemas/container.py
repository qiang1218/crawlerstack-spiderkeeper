"""
Container schema
"""
from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module


class ContainerSchema(BaseModel):
    """Executor base schema."""
    container_id: constr(max_length=200) = None
    status: constr(max_length=20) = None
    task_name: constr(max_length=100) = None
