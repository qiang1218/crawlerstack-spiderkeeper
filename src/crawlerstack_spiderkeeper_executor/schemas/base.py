"""
Base schema.
"""
from typing import Any

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class SpiderSchema(BaseModel):
    """Spider"""
    DATA_URL: str
    LOG_URL: str
    METRICS: str
    STORAGE_ENABLE: bool
    TASK_NAME: str


class ExecutorSchema(BaseModel):
    """Executor"""
    image: str
    cmdline: str
    volume: list | None
    environment: list | None


class TaskSchema(BaseModel):
    """Task"""
    spider_params: SpiderSchema
    executor_params: ExecutorSchema
