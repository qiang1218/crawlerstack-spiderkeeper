"""Job"""
from typing import Union, Dict, Any

from crawlerstack_spiderkeeper_server.repository.artifact import ArtifactRepository
from crawlerstack_spiderkeeper_server.repository.storage_server import StorageServerRepository
from crawlerstack_spiderkeeper_server.schemas.artifact import ArtifactSchema
from crawlerstack_spiderkeeper_server.schemas.storage_server import StorageServerSchema
from crawlerstack_spiderkeeper_server.services.base import EntityService
from crawlerstack_spiderkeeper_server.models import Job
from crawlerstack_spiderkeeper_server.schemas.job import (JobCreate, JobUpdate, JobSchema)
from crawlerstack_spiderkeeper_server.repository.job import JobRepository
from crawlerstack_spiderkeeper_server.utils.exceptions import JobStoppedError, JobRunError, JobPauseError, \
    JobUnpauseError
from crawlerstack_spiderkeeper_server.utils.types import CreateSchemaType, ModelSchemaType, UpdateSchemaType

from crawlerstack_spiderkeeper_server.utils.request import RequestWithSession
from crawlerstack_spiderkeeper_server.config import settings


class JobService(EntityService[Job, JobCreate, JobUpdate, JobSchema]):
    """
    Job service.
    """
    REPOSITORY_CLASS = JobRepository

    @property
    def artifact_repository(self):
        """artifact repository"""
        return ArtifactRepository()

    @property
    def storage_server_repository(self):
        """storage server repository"""
        return StorageServerRepository()

    @property
    def request_session(self):
        """request"""
        return RequestWithSession()

    @property
    def start_url(self):
        """start url"""
        return settings.SCHEDULER_URL + settings.SCHEDULER_START_SUFFIX

    @property
    def stop_url(self):
        """stop url"""
        return settings.SCHEDULER_URL + settings.SCHEDULER_STOP_SUFFIX

    @property
    def pause_url(self):
        """pause url"""
        return settings.SCHEDULER_URL + settings.SCHEDULER_PAUSE_SUFFIX

    @property
    def unpause_url(self):
        """unpause url"""
        return settings.SCHEDULER_URL + settings.SCHEDULER_UNPAUSE_SUFFIX

    async def create(
            self,
            *,
            obj_in: CreateSchemaType
    ) -> ModelSchemaType:
        """
        Create a record.
        :param obj_in:
        :return:
        """
        # 默认情况下，任务添加时的逻辑不进行任务调用触发，由单独的任务开关进行处理
        obj_in.enabled = False
        obj_in.pause = False
        await self.artifact_repository.exists(obj_in.artifact_id)
        await self.storage_server_repository.exists(obj_in.storage_server_id)
        return await self.repository.create(obj_in=obj_in)

    async def update_by_id(
            self,
            pk: int,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelSchemaType:
        """
        Update a record.
        :param pk:
        :param obj_in:
        :return:
        """
        # 默认情况下，任务添加时的逻辑不进行任务调用触发，由单独的任务开关进行处理
        obj_in.enabled = False
        obj_in.pause = False
        artifact_id = obj_in.artifact_id
        if artifact_id is not None:
            await self.artifact_repository.exists(obj_in.artifact_id)
        storage_server_id = obj_in.storage_server_id
        if storage_server_id is not None:
            await self.storage_server_repository.exists(obj_in.storage_server_id)
        return await self.repository.update_by_id(pk=pk, obj_in=obj_in)

    async def run_by_id(self, pk: int):
        """
        Run by id
        :param pk:
        :return:
        """
        # 1. 任务数据库获取
        job = await self.repository.get_by_id(pk=pk)
        # 2. 状态一致性判断
        if not job.enabled:
            # 3. 调用调度器接口
            resp = self.request_session.request('GET', self.start_url % pk)
            if resp.get('message') == 'ok':
                # 4. 数据库状态修改
                return await self.repository.update_by_id(pk=pk, obj_in=dict(enabled=True, pause=False))
            return {'message': 'Job start Scheduler failed, job id: %s, exception info: %s' % (pk, resp.get('message'))}

        raise JobRunError()

    async def stop_by_id(self, pk: int) -> Any:
        """
        Stop by id
        :param pk:
        :return:
        """
        # 1. 任务数据获取
        job = await self.repository.get_by_id(pk=pk)
        # 2. 状态一致性判断
        if job.enabled:
            # 3. 接口调用
            resp = self.request_session.request('GET', self.stop_url % pk)
            if resp.get('message') == 'ok':
                # 数据库状态修改
                return await self.repository.update_by_id(pk=pk, obj_in=dict(enabled=False, pause=False))
            return {'message': 'Job stop failed, job id: %s, exception info: %s' % (pk, resp.get('message'))}

        raise JobStoppedError()

    async def pause_by_id(self, pk: int):
        """
        pause by id
        :param pk:
        :return:
        """
        # 1. 任务数据获取
        job = await self.repository.get_by_id(pk=pk)
        # 2. 状态一致性判断
        if job.enabled and not job.pause:
            # 3. 接口调用
            resp = self.request_session.request('GET', self.pause_url % pk)
            if resp.get('message') == 'ok':
                # 数据库状态修改
                return await self.repository.update_by_id(pk=pk, obj_in=dict(pause=True))
            return {'message': 'Job pause failed, job id: %s, exception info: %s' % (pk, resp.get('message'))}

        raise JobPauseError()

    async def unpause_by_id(self, pk: int):
        """
        unpause by id
        :param pk:
        :return:
        """
        # 1. 任务数据获取
        job = await self.repository.get_by_id(pk=pk)
        # 2. 状态一致性判断
        if job.enabled and job.pause:
            # 3. 接口调用
            resp = self.request_session.request('GET', self.unpause_url % pk)
            if resp.get('message') == 'ok':
                # 数据库状态修改
                return await self.repository.update_by_id(pk=pk, obj_in=dict(pause=False))
            return {'message': 'Job unpause failed, job id: %s, exception info: %s' % (pk, resp.get('message'))}

        raise JobUnpauseError()

    async def get_artifact_from_job_id(self, pk: int) -> ArtifactSchema:
        """
        get a artifact from job id
        :param pk:
        :return:
        """
        return await self.artifact_repository.get_artifact_from_job_id(pk)

    async def get_storage_server_from_job_id(self, pk: int) -> StorageServerSchema:
        """
        get a storage server from job id
        :param pk:
        :return:
        """
        return await self.storage_server_repository.get_storage_server_from_job_id(pk)
