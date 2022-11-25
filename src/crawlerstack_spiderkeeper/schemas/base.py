"""
Base schema.
"""
from pydantic import BaseModel  # pylint: disable=no-name-in-module


class InDBMixin(BaseModel):
    """Db model mixin."""
    id: int

    class Config:
        """Model ORM config"""
        orm_mode = True
