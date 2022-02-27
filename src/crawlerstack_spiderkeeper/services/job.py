"""
Job service.
"""
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.dao import ArtifactDAO, JobDAO, TaskDAO
from crawlerstack_spiderkeeper.db.models import Job, Task
from crawlerstack_spiderkeeper.executor import executor_factory
from crawlerstack_spiderkeeper.schemas import ActionResult
from crawlerstack_spiderkeeper.schemas.artifact import ArtifactUpdate
from crawlerstack_spiderkeeper.schemas.job import JobCreate, JobUpdate
from crawlerstack_spiderkeeper.schemas.task import TaskCreate, TaskUpdate
from crawlerstack_spiderkeeper.services.base import EntityService
from crawlerstack_spiderkeeper.utils import (AppId, ArtifactMetadata)
from crawlerstack_spiderkeeper.utils.exceptions import UnprocessableEntityError
from crawlerstack_spiderkeeper.utils.status import Status

logger = logging.getLogger(__name__)


class JobService(EntityService[Job, JobCreate, JobUpdate]):
    """
    Job service
    """
    DAO_CLASS = JobDAO

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._job_dao = JobDAO(self.session)
        self._artifact_dao = ArtifactDAO(self.session)
        self._task_dao = TaskDAO(self.session)

        self.executor_cls = executor_factory()

    @property
    def artifact_dao(self) -> ArtifactDAO:
        return self._artifact_dao

    @property
    def task_dao(self) -> TaskDAO:
        return self._task_dao

    @property
    def job_dao(self) -> JobDAO:
        return self._job_dao

    async def status(self, pk: int) -> str:
        """
        Job status
        :param pk:
        :return:
        """
        status = await self.dao.status(pk=pk)
        if status:
            return status.name

    async def run(self, pk: int) -> ActionResult:
        """
        运行 Job
        :param pk:
        :return:
        """
        obj = await self.dao.get_by_id(pk)
        artifact = await self.artifact_dao.get_by_id(obj.artifact_id)
        artifact_meta = ArtifactMetadata(artifact.filename)

        running_task_count = await self.task_dao.count_running_task(pk)

        if running_task_count:
            result = ActionResult(
                success=False,
                message='Job already run.',
            )
            raise UnprocessableEntityError(detail=result.dict())

        task = await self.task_dao.create(obj_in=TaskCreate(job_id=pk))
        await self._build_context(job_id=pk, artifact_meta=artifact_meta)
        # TODO 优化 obj.cmdline 数据因 ` ` 分隔符造成错误。将此数据改为json即可，但要做格式判断
        # 如果需要执行 `python -c "for i in range(10): print(i)"` 用空格分割就会出现问题
        await self._run_task(task, artifact_meta, cmdline=obj.cmdline.split(' '))
        logger.debug('<%s> is start', obj)
        return ActionResult(success=True, message='Job running.')

    async def _build_context(self, job_id: int, artifact_meta: ArtifactMetadata):
        """如果执行环境不存在，则构建"""
        executor_context = self.executor_cls.executor_context(artifact_meta)
        artifact = await self.artifact_dao.get_artifact_from_job_id(job_id=job_id)

        # 之后环境存在，并且数据库状态为完成时，才不重新构建
        if await executor_context.exist() and artifact.status == Status.FINISH.value:
            logger.debug('%s context had exist, skip build.', artifact_meta)
        else:
            logger.debug('%s context not exist, building...', artifact_meta)
            # 更新 Job 状态
            await self.artifact_dao.update(
                db_obj=artifact,
                obj_in=ArtifactUpdate(status=Status.BUILDING.value)
            )

            try:
                await executor_context.build()
            except Exception as ex:
                logger.debug('%s context build failure. %s', artifact_meta, ex)
                await self.artifact_dao.update(
                    db_obj=artifact,
                    obj_in=ArtifactUpdate(status=Status.FAILURE.value)
                )
                raise ex
            await self.artifact_dao.update(
                db_obj=artifact,
                obj_in=ArtifactUpdate(status=Status.FINISH.value)
            )
            logger.debug('%s context build finish.', artifact_meta)

    async def _run_task(
            self,
            task: Task,
            artifact_meta: ArtifactMetadata,
            cmdline: List[str]
    ) -> None:
        """启动 Spider 容器任务，并更新 task 状态"""
        app_id = AppId(job_id=task.job_id, task_id=task.id)
        executor = await self.executor_cls.run(
            artifact=artifact_meta,
            cmdline=cmdline,
            env={
                'SPIDERKEEPER_APPID': str(app_id),
                'SPIDERKEEPER_HOST_ADDR': settings.HOST_ADDR,
                'ENABLE_SPIDERKEEPER_SUPPORT': 'True',
            }
        )
        # Update task
        await self.task_dao.update(
            db_obj=task,
            obj_in=TaskUpdate(container_id=executor.pid, status=Status.RUNNING.value)
        )
        logger.debug('%s is running...', app_id)

    async def stop(self, pk: int) -> ActionResult:
        """
        Stop job.
        :param pk:
        :return:
        """
        obj = await self._job_dao.get_by_id(pk)
        artifact = await self.artifact_dao.get_by_id(obj.artifact_id)
        artifact_meta = ArtifactMetadata(artifact.filename)

        running_task_count = await self.task_dao.count_running_task(pk)

        running_tasks = await self.task_dao.get_running(
            job_id=pk,
            limit=running_task_count
        )

        if running_tasks:
            task_ids = []
            # 更新 task 状态为正在停止
            for task in running_tasks:  # type: Task
                task_ids.append(task.id)
                # 停止 task
                try:
                    executor = self.executor_cls(artifact_meta, task.container_id)
                    await executor.stop()
                    status = Status.STOPPED.value
                    detail = 'Stopped.'
                except Exception as ex:  # pylint: disable=broad-except
                    # FIXME task 可能无法正确停止，但结果已经标记失败。
                    # 为了记录无法预知的错误情况而捕获异常信息，并记录
                    status = Status.FAILURE.value
                    detail = f'Stop fail. {str(ex)}'
                    logger.error(detail)
                await self.task_dao.update_by_id(
                    pk=task.id,
                    obj_in=TaskUpdate(status=status, detail=detail)
                )

            return ActionResult(
                success=True,
                message='Task stopped.'
            )
        result = ActionResult(
            success=False,
            message='No task run.',
        )
        raise UnprocessableEntityError(detail=result.dict())
