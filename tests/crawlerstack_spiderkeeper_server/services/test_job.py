"""test job"""
import inspect

import pytest

from crawlerstack_spiderkeeper_server.schemas.job import JobCreate, JobUpdate
from crawlerstack_spiderkeeper_server.services.job import JobService
from crawlerstack_spiderkeeper_server.utils.exceptions import (
    JobPauseError, JobRunError, JobStoppedError, JobUnpauseError,
    ObjectDoesNotExist)
from crawlerstack_spiderkeeper_server.utils.request import RequestWithHttpx


@pytest.fixture()
def service():
    """service fixture"""
    return JobService()


@pytest.mark.parametrize(
    'artifact_id, storage_server_id, exist',
    [
        (1, 1, True),
        (100, 100, False)
    ]
)
async def test_create(init_artifact, init_storage_server, session, service, artifact_id, storage_server_id, exist):
    """test create"""
    obj_in = JobCreate(name="test1", trigger_expression="0 0 * * *", storage_enable=True, executor_type='docker',
                       storage_server_id=storage_server_id, snapshot_enable=False, snapshot_server_id=storage_server_id,
                       artifact_id=artifact_id, enabled=False, pause=False)
    if exist:
        await service.create(obj_in=obj_in)
        count = await service.count()
        assert count == 1
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.create(obj_in=obj_in)


@pytest.mark.parametrize(
    'pk, artifact_id, storage_server_id, exist',
    [
        (1, 2, 2, True),
        (1, 2, 100, False),
        (1, 100, 2, False),
        (1, 100, 100, False),
        (100, 100, 100, False)
    ]
)
async def test_update_by_id(init_job, session, service, pk, artifact_id, storage_server_id, exist):
    """test update by id"""
    obj_in = JobUpdate(artifact_id=artifact_id, storage_server_id=storage_server_id)
    if exist:
        before = await service.get_by_id(pk)
        await service.update_by_id(pk, obj_in=obj_in)
        after = await service.get_by_id(pk)
        assert before
        assert after.artifact_id != before.artifact_id
        assert after.artifact_id == obj_in.artifact_id
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.update_by_id(pk, obj_in=obj_in)


@pytest.mark.parametrize(
    'pk, artifact_name, exist',
    [
        (1, 'test1', True),
        (100, None, False)
    ]
)
async def test_get_artifact_from_job_id(init_job, session, service, pk, artifact_name, exist):
    """test get a artifact from job id"""
    if exist:
        result = await service.get_artifact_from_job_id(pk)
        assert result
        assert result.name == artifact_name
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.get_artifact_from_job_id(pk)


@pytest.mark.parametrize(
    'pk, storage_server_name, exist',
    [
        (1, 'test1', True),
        (100, None, False)
    ]
)
async def test_get_storage_server_from_job_id(init_job, session, service, pk, storage_server_name, exist):
    """test get a storage server from job id"""
    if exist:
        result = await service.get_storage_server_from_job_id(pk)
        assert result
        assert result.name == storage_server_name
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.get_storage_server_from_job_id(pk)


@pytest.mark.parametrize(
    'pk, expect_value',
    [
        (1, 'True'),
        (2, JobRunError),
        (100, ObjectDoesNotExist)
    ]
)
async def test_run_by_id(init_job, session, service, mocker, pk, expect_value):
    """test run by id"""
    if inspect.isclass(expect_value):
        mocker.patch.object(RequestWithHttpx, 'request', return_value={'detail': 'failure'})
        with pytest.raises(expect_value):
            await service.run_by_id(pk)
    else:
        request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'message': 'success'})
        await service.run_by_id(pk)
        request.assert_called_once()


@pytest.mark.parametrize(
    'pk, expect_value',
    [
        (1, 'True'),
        (2, JobRunError),
        (100, ObjectDoesNotExist)
    ]
)
async def test_start_by_id(init_job, session, service, mocker, pk, expect_value):
    """test run by id"""
    request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'message': 'success'})
    if inspect.isclass(expect_value):
        with pytest.raises(expect_value):
            await service.start_by_id(pk)
    else:
        obj = await service.start_by_id(pk)
        assert obj.enabled
        request.assert_called_once()


@pytest.mark.parametrize(
    'pk, expect_value',
    [
        (1, JobStoppedError),
        (2, 'True'),
        (100, ObjectDoesNotExist)
    ]
)
async def test_stop_by_id(init_job, session, service, mocker, pk, expect_value):
    """test stop by id"""
    request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'message': 'success'})
    if inspect.isclass(expect_value):
        with pytest.raises(expect_value):
            await service.stop_by_id(pk)
    else:
        obj = await service.stop_by_id(pk)
        assert not obj.enabled
        request.assert_called_once()


@pytest.mark.parametrize(
    'pk, expect_value',
    [
        (1, JobPauseError),
        (2, 'True'),
        (100, ObjectDoesNotExist)
    ]
)
async def test_pause_by_id(init_job, session, service, mocker, pk, expect_value):
    """test pause by id"""
    request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'message': 'success'})
    if inspect.isclass(expect_value):
        with pytest.raises(expect_value):
            await service.pause_by_id(pk)
    else:
        obj = await service.pause_by_id(pk)
        assert obj.enabled
        assert obj.pause
        request.assert_called_once()


@pytest.mark.parametrize(
    'pk, expect_value',
    [
        (1, JobUnpauseError),
        (2, JobUnpauseError),
        (3, 'True'),
        (100, ObjectDoesNotExist)
    ]
)
async def test_unpause_by_id(init_job, session, service, mocker, pk, expect_value):
    """test unpause by id"""
    request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'message': 'success'})
    if inspect.isclass(expect_value):
        with pytest.raises(expect_value):
            await service.unpause_by_id(pk)
    else:
        obj = await service.unpause_by_id(pk)
        assert obj.enabled
        assert not obj.pause
        request.assert_called_once()
