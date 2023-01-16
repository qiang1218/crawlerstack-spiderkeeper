"""test job"""
import pytest

from crawlerstack_spiderkeeper_scheduler.services import SchedulerServer
from crawlerstack_spiderkeeper_scheduler.services.job import JobService


class TestJobService:
    """Test job service"""

    @pytest.fixture()
    def service(self):
        """service fixture"""
        return JobService()

    @pytest.fixture()
    def job_data(self):
        """job data fixture"""
        return {
            "id": 0,
            "update_time": "2023-01-09T06:27:05.244Z",
            "create_time": "2023-01-09T06:27:05.244Z",
            "name": "string",
            "cmdline": "string",
            "environment": "string",
            "volume": "string",
            "trigger_expression": "string",
            "storage_enable": False,
            "storage_server_id": 0,
            "executor_type": "string",
            "enabled": False,
            "pause": False,
            "executor_selector": "string",
            "artifact_id": 0
        }

    @pytest.fixture()
    def artifact_data(self):
        """artifact data fixture"""
        return {
            "id": 0,
            "update_time": "2023-01-09T06:25:03.225Z",
            "create_time": "2023-01-09T06:25:03.225Z",
            "name": "string",
            "desc": "string",
            "image": "string",
            "tag": "string",
            "version": "latest",
            "project_id": 0
        }

    @pytest.mark.parametrize(
        'job_id',
        [
            ('1',),
        ]
    )
    def test_start_by_id(self, mocker, service, job_id, job_data, artifact_data):
        """test start by id"""

        get_job = mocker.patch.object(JobService, 'get_job', return_value=job_data)
        get_artifact = mocker.patch.object(JobService, 'get_artifact', return_value=artifact_data)
        add_job = mocker.patch.object(SchedulerServer, 'add_job')
        service.start_by_id(job_id=job_id)

        get_job.assert_called_once()
        get_artifact.assert_called_once()
        add_job.assert_called_once()

    @pytest.mark.parametrize(
        'job_id',
        [
            ('1',),
        ]
    )
    def test_stop_by_id(self, mocker, service, job_id):
        """test stop by id"""
        remove_job = mocker.patch.object(SchedulerServer, 'remove_job')
        service.stop_by_id(job_id=job_id)
        remove_job.assert_called_once()

    @pytest.mark.parametrize(
        'job_id',
        [
            ('1',),
        ]
    )
    def test_pause_by_id(self, mocker, service, job_id):
        """test pause by id"""
        pause_job = mocker.patch.object(SchedulerServer, 'pause_job')
        service.pause_by_id(job_id=job_id)
        pause_job.assert_called_once()

    @pytest.mark.parametrize(
        'job_id',
        [
            ('1',),
        ]
    )
    def test_unpause_by_id(self, mocker, service, job_id):
        """test pause by id"""
        unpause_job = mocker.patch.object(SchedulerServer, 'unpause_job')
        service.unpause_by_id(job_id=job_id)
        unpause_job.assert_called_once()
