"""scheduler"""
import logging
from typing import Union

import pytz
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job

from crawlerstack_spiderkeeper_scheduler.config import settings
from crawlerstack_spiderkeeper_scheduler.utils import SingletonMeta

from crawlerstack_spiderkeeper_scheduler.services.task import TaskService
from crawlerstack_spiderkeeper_scheduler.tasks.task import Task

logger = logging.getLogger(__name__)


class SchedulerServer(metaclass=SingletonMeta):

    def __init__(self, *args, **kwargs):
        self.apscheduler = AsyncIOScheduler(timezone=pytz.timezone(settings.SCHEDULER_TIMEZONE))
        self.apscheduler.configure()
        self.task = Task(settings)

    @property
    def task_service(self):
        return TaskService()

    def start(self):
        # 根据环境变量,初始化对应的参数
        jobstores = {
            'default': SQLAlchemyJobStore(url=settings.SCHEDULER_JOB_STORE_DEFAULT)
        }
        executors = {
            'default': ThreadPoolExecutor(settings.SCHEDULER_EXECUTORS_DEFAULT_COUNT),
        }
        job_defaults = {
            'coalesce': False if settings.SCHEDULER_JOB_DEFAULTS_COALESCE.lower() == 'false' else True,
            'max_instances': settings.SCHEDULER_JOB_DEFAULTS_MAX_INSTANCES
        }

        self.apscheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
        self.apscheduler.start()

    def add_job(self, job_id: str, trigger_expression: str, **kwargs):
        """
        添加job
        :param job_id:
        :param trigger_expression:
        :param kwargs:
        :return:
        """
        logger.debug('Add job %s to scheduler', job_id)
        self.apscheduler.add_job(
            func=self.task.run,
            trigger=CronTrigger.from_crontab(trigger_expression),
            kwargs=kwargs,
            id=job_id,
        )

    def remove_job(self, job_id: str):
        """
        remove job
        :param job_id:
        :return:
        """
        logger.debug('Remove job %s from scheduler', job_id)
        self.apscheduler.remove_job(job_id=job_id)

    def get_apscheduler_jobs(self, job_id: str = None) -> Union[list[Job], Job, None]:
        """
        get apscheduler jobs
        :param job_id:
        :return:
        """
        # todo 暂时不做两边状态的判断
        if job_id:
            return self.apscheduler.get_job(job_id=job_id)
        return self.apscheduler.get_jobs()

    def pause_job(self, job_id: str):
        """
        pause job
        :param job_id:
        :return:
        """
        # 任务暂停执行
        self.apscheduler.pause_job(job_id=job_id)

    def unpause_job(self, job_id: str):
        """
        unpause job
        :param job_id:
        :return:
        """
        # 任务恢复执行
        self.apscheduler.resume_job(job_id=job_id)

    def stop(self):
        self.apscheduler.shutdown(wait=False)
