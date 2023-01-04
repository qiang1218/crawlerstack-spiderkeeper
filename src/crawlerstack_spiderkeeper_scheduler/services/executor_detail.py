"""Executor detail"""

from crawlerstack_spiderkeeper_scheduler.services.base import EntityService
from crawlerstack_spiderkeeper_scheduler.models import ExecutorDetail
from crawlerstack_spiderkeeper_scheduler.schemas.executor_detail import (ExecutorDetailCreate, ExecutorDetailUpdate,
                                                                         ExecutorDetailSchema)
from crawlerstack_spiderkeeper_scheduler.repository.executor_detail import ExecutorDetailRepository


class ExecutorDetailService(EntityService[ExecutorDetail, ExecutorDetailCreate, ExecutorDetailUpdate,
                                          ExecutorDetailSchema]):
    """
    Executor detail service.
    """
    REPOSITORY_CLASS = ExecutorDetailRepository
