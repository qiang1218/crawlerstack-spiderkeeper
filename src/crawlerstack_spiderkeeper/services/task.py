"""
Task service
"""
from crawlerstack_spiderkeeper.dao import TaskDAO
from crawlerstack_spiderkeeper.services.base import BaseService


class TaskService(BaseService):
    """
    Task service.
    """
    DAO_CLASS = TaskDAO
