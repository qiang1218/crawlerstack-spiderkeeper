"""test scheduler"""
import asyncio

import pytest

from crawlerstack_spiderkeeper_scheduler.services import SchedulerServer


async def task(**_):
    """task"""
    for i in range(10):
        await asyncio.sleep(0)


class TestJobService:

    @pytest.fixture()
    def service(self, settings):
        """service fixture"""
        return SchedulerServer(settings)

    def test_add_job(self, service):
        """test add job"""
        self.clear_job(service)
        service.add_job(func=task, job_id='task_1', trigger_expression='0 0 1 * *')
        added_jobs = service.get_apscheduler_jobs()
        assert len(added_jobs) == 1

    @staticmethod
    def clear_job(service):
        """clear job method"""
        added_jobs = service.get_apscheduler_jobs()
        for job in added_jobs:
            service.remove_job(job.id)
