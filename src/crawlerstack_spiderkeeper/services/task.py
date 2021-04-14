"""
Task service
"""
from crawlerstack_spiderkeeper.dao import task_dao
from crawlerstack_spiderkeeper.services.base import BaseService


class TaskService(BaseService):
    """
    Task service.
    """
    dao = task_dao
