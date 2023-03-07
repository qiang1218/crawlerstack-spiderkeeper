"""
Base schema.
"""
from datetime import datetime

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class InDBMixin(BaseModel):
    """Db model mixin."""
    id: int
    update_time: datetime = None
    create_time: datetime = None

    class Config:
        """Model ORM config"""
        orm_mode = True
        arbitrary_types_allowed = True


class SpiderSchema(BaseModel):
    """Spider"""
    DATA_URL: str
    LOG_URL: str
    METRICS_URL: str
    STORAGE_ENABLE: bool
    SNAPSHOT_ENABLE: bool
    TASK_NAME: str


class ExecutorSchema(BaseModel):
    """Executor"""
    image: str
    cmdline: str | list
    volume: list | None
    environment: list | None
    executor_selector: str | None
    executor_type: str | None
