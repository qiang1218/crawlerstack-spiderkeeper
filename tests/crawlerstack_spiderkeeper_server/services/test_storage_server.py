"""Test storage server"""
import pytest

from crawlerstack_spiderkeeper_server.services import StorageServerService
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist


@pytest.fixture()
def service():
    """service fixture"""
    return StorageServerService()


@pytest.mark.parametrize(
    'pk, storage_server_name, exist',
    [
        (1, 'test1', True),
        (100, None, False)
    ]
)
async def test_get_storage_server_from_job_id(init_job, session, service, pk, storage_server_name, exist):
    """test get_storage_server_from_job_id"""
    if exist:
        result = await service.get_storage_server_from_job_id(pk)
        assert result
        assert result.name == storage_server_name
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.get_storage_server_from_job_id(pk)


@pytest.mark.parametrize(
    'pk, storage_server_name, exist',
    [
        (1, 'test1', True),
        (100, None, False)
    ]
)
async def test_get_snapshot_server_from_job_id(init_job, session, service, pk, storage_server_name, exist):
    """test get_snapshot_server_from_job_id"""
    if exist:
        result = await service.get_snapshot_server_from_job_id(pk)
        assert result
        assert result.name == storage_server_name
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.get_snapshot_server_from_job_id(pk)
