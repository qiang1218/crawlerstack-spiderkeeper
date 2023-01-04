"""Executor detail"""

from crawlerstack_spiderkeeper_scheduler.repository.base import BaseRepository

from crawlerstack_spiderkeeper_scheduler.models import ExecutorDetail
from crawlerstack_spiderkeeper_scheduler.schemas.executor_detail import (ExecutorDetailCreate, ExecutorDetailUpdate,
                                                                         ExecutorDetailSchema)


class ExecutorDetailRepository(BaseRepository[ExecutorDetail, ExecutorDetailCreate, ExecutorDetailUpdate,
                                              ExecutorDetailSchema]):
    """executor detail repository"""
    model = ExecutorDetail
    model_schema = ExecutorDetailSchema
