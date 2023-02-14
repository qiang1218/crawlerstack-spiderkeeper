"""scheduler"""
import logging
from typing import Union

import pytz
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from crawlerstack_spiderkeeper_scheduler.utils import SingletonMeta

logger = logging.getLogger(__name__)


class SchedulerServer(metaclass=SingletonMeta):
    """Scheduler server"""

    def __init__(self, settings):
        self.settings = settings
        # 根据环境变量,初始化对应的参数
        jobstores = {
            'default': SQLAlchemyJobStore(url=self.settings.SCHEDULER_JOB_STORE_DEFAULT)
        }
        job_defaults = {
            'coalesce': self.settings.SCHEDULER_JOB_DEFAULTS_COALESCE,
            'max_instances': self.settings.SCHEDULER_JOB_DEFAULTS_MAX_INSTANCES
        }

        self.apscheduler = AsyncIOScheduler(jobstores=jobstores,
                                            job_defaults=job_defaults,
                                            timezone=pytz.timezone(self.settings.SCHEDULER_TIMEZONE))

    def start(self):
        """start"""
        self.apscheduler.start()

    def add_job(self, func, trigger_expression: str, **kwargs):
        """
        添加job
        :param func:
        :param trigger_expression:
        :param kwargs:
        :return:
        """
        job_id = kwargs.get('job_id')
        logger.debug('Add job %s to scheduler', job_id)
        self.apscheduler.add_job(
            func=func,
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

    def clear_jobs(self):
        """clear job method"""
        added_jobs = self.get_apscheduler_jobs()
        for job in added_jobs:
            self.remove_job(job.id)

    def stop(self):
        """stop"""
        self.apscheduler.shutdown(wait=False)
