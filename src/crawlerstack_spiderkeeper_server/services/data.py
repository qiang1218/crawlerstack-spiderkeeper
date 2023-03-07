"""data"""

import logging
from typing import Any

from fastapi_sa.database import session_ctx

from crawlerstack_spiderkeeper_server.data_storage import StorageFactory
from crawlerstack_spiderkeeper_server.repository.job import JobRepository
from crawlerstack_spiderkeeper_server.repository.storage_server import \
    StorageServerRepository
from crawlerstack_spiderkeeper_server.repository.task import TaskRepository
from crawlerstack_spiderkeeper_server.repository.task_detail import \
    TaskDetailRepository
from crawlerstack_spiderkeeper_server.schemas.job import JobSchema
from crawlerstack_spiderkeeper_server.schemas.storage_server import \
    StorageServerSchema
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

    @session_ctx
    async def create(self, task_name: str, data: dict) -> None:
        """Create data"""
        # 1.根据task_name获取对应的task_id
        job = await self.job_repository.get_job_from_task_name(task_name)

        # 快照和具体的内容区分，进而确定具体的更新策略
        snapshot_enabled = data.get('snapshot_enabled')
        if snapshot_enabled:
            await self.handle_snapshot_data(job, task_name, data)
        else:
            await self.handle_structured_data(job, task_name, data)

    async def handle_structured_data(self, job: JobSchema, task_name: str, data: dict):
        """
        Handle structured data
        :param job:
        :param task_name:
        :param data:
        :return:
        """
        if not job.storage_enable:
            logger.debug("Data storage enabled is false, task_name is %s", task_name)
            return
        storage_server = await self.storage_server_repository.get_storage_server_from_job_id(job.id)
        status = await self.storage_data(storage_server, data)
        data_count = len(data.get('datas'))
        fields = 'item_count'
        await self.create_or_update_task_detail(task_name, data_count, status, fields)

    async def handle_snapshot_data(self, job: JobSchema, task_name: str, data: dict):
        """
        Handle snapshot data
        :param job:
        :param task_name:
        :param data:
        :return:
        """
        if not job.snapshot_enable:
            logger.debug("Snapshot storage enabled is false, task_name is %s", task_name)
            return
        storage_server = await self.storage_server_repository.get_snapshot_server_from_job_id(job.id)
        status = await self.storage_data(storage_server, data)
        # 快照的计数通常为1，即不对多组数据叠加处理
        data_count = 1
        # 获取task_name对应的task_detail,将条数更新
        fields = 'snapshot_count'
        await self.create_or_update_task_detail(task_name, data_count, status, fields)

    @staticmethod
    async def storage_data(storage_server: StorageServerSchema, data: dict) -> bool:
        """
        Storage data
        :param storage_server:
        :param data:
        :return:
        """
        name = storage_server.name
        storage_class = storage_server.storage_class
        url = storage_server.url
        return await StorageFactory().get_storage(storage_class, name, url).save(data)

    async def create_or_update_task_detail(self, task_name: str, data_count: int, status: bool, fields: str):
        """
        Create or update task detail
        :param task_name:
        :param data_count:
        :param status:
        :param fields: updates to distinguish between different fields
        :return:
        """
        # 获取task_name对应的task_id
        try:
            task = await self.task_repository.get_by_name(name=task_name)
            task_id = task.id
        except ObjectDoesNotExist:
            logger.warning('Task data is not exist, task_name is %s', task_name)
        else:
            try:
                task_details = await self.task_detail_repository.get(search_fields={'task_id': task_id})
                # task 与 task_detail 一对一关系
                _task_detail = task_details[0]
                data = {
                    'detail': str(status),
                    fields: _task_detail.dict().get(fields) + data_count
                }
                await self.task_detail_repository.update_by_id(pk=_task_detail.id, obj_in=TaskDetailUpdate(**data))
            except ObjectDoesNotExist:
                data = {
                    'task_id': task_id,
                    'detail': str(status),
                    fields: data_count
                }
                await self.task_detail_repository.create(obj_in=TaskDetailCreate(**data))

    async def update(self, *args, **kwargs) -> Any:
        """Update"""

    async def delete(self, *args, **kwargs) -> Any:
        """Delete"""
