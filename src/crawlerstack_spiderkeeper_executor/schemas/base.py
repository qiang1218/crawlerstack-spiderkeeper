"""
Base schema.
"""
from pydantic import BaseModel  # pylint: disable=no-name-in-module


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
    cmdline: list
    volume: list | None
    environment: list | None
    cpu_limit: int
    memory_limit: int


class TaskSchema(BaseModel):
    """Task"""
    spider_params: SpiderSchema
    executor_params: ExecutorSchema
