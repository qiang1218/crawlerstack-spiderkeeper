"""
Task service
"""
from crawlerstack_spiderkeeper.dao import TaskDAO
from crawlerstack_spiderkeeper.services.base import EntityService


class TaskService(EntityService):
    """
    Task service.
    """
    DAO_CLASS = TaskDAO
