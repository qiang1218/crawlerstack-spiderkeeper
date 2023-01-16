"""data"""

import logging
from typing import Any

from crawlerstack_spiderkeeper_server.data_storage import StorageFactory
from crawlerstack_spiderkeeper_server.repository.job import JobRepository
from crawlerstack_spiderkeeper_server.repository.storage_server import \
    StorageServerRepository
from crawlerstack_spiderkeeper_server.repository.task import TaskRepository
from crawlerstack_spiderkeeper_server.repository.task_detail import \
    TaskDetailRepository
from crawlerstack_spiderkeeper_server.schemas.task_detail import (
    TaskDetailCreate, TaskDetailUpdate)
from crawlerstack_spiderkeeper_server.services.base import ICRUD
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist

logger = logging.getLogger(__name__)


class DataService(ICRUD):
    """Data service"""
    async def get(self, query):
        """Get"""
        # 暂时不提供get数据接口

    @property
    def job_repository(self):
        """Job repository"""
        return JobRepository()

    @property
    def storage_server_repository(self):
        """Storage server repository"""
        return StorageServerRepository()

    @property
    def task_repository(self):
        """Task repository"""
        return TaskRepository()

    @property
    def task_detail_repository(self):
        """Task detail repository"""
        return TaskDetailRepository()

    async def create(self, task_name: str, data: dict) -> None:
        """Create data"""
        # 1.根据task_name获取对应的task_id
        job = await self.job_repository.get_job_from_task_name(task_name)

        # 2.根据task_id获取job_id, 对storage_enable判断， 保存时，获取storage_server信息
        if not job.storage_enable:
            logger.debug("Storage enabled is false, task_name is %s", task_name)
            return

        # 3.根据storage_server的storage_class 和 uri确定存储的实现逻辑
        storage_server = await self.storage_server_repository.get_storage_server_from_job_id(job.storage_server_id)

        # 4.保存数据
        name = storage_server.name
        storage_class = storage_server.storage_class
        url = storage_server.url
        status = StorageFactory().get_storage(storage_class, name, url).save(data)

        # 5.同时计算数据量，将task_detail表的数据进行填充更新操作,完毕后退出
        data_count = len(data.get('datas'))
        # 获取task_name对应的task_detail,将条数更新
        await self.create_or_update_task_detail(task_name, data_count, status)

    async def create_or_update_task_detail(self, task_name: str, data_count: int, status: bool):
        """
        Create or update task detail
        :param task_name:
        :param data_count:
        :param status:
        :return:
        """
        # 获取task_name对应的task_id
        task_id = 0
        try:
            task = await self.task_repository.get(search_fields={'name': task_name})
            task_id = task[0].id
        except ObjectDoesNotExist:
            logger.warning('Task data is not exist, task_name is %s', task_name)

        try:
            task_details = await self.task_detail_repository.get(search_fields={'task_id': task_id})
            # task 与 task_detail 一对一关系
            _task_detail = task_details[0]
            _task_detail.item_count += data_count
            task_detail = TaskDetailUpdate(item_count=_task_detail.item_count, detail=str(status))
            await self.task_detail_repository.update_by_id(pk=_task_detail.id, obj_in=task_detail)
        except ObjectDoesNotExist:
            task_detail = TaskDetailCreate(task_id=task_id, item_count=data_count, detail=str(status))
            await self.task_detail_repository.create(obj_in=task_detail)

    async def update(self, *args, **kwargs) -> Any:
        """Update"""

    async def delete(self, *args, **kwargs) -> Any:
        """Delete"""
