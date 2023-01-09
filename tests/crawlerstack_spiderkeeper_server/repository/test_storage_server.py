"""test storage server"""
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawlerstack_spiderkeeper_server.models import Job

from crawlerstack_spiderkeeper_server.utils.exceptions import ObjectDoesNotExist
from crawlerstack_spiderkeeper_server.repository.storage_server import StorageServerRepository


@pytest.fixture()
async def repo():
    """repo fixture"""
    return StorageServerRepository()


@pytest.mark.parametrize(
    'job_id, exist',
    [
        (1, True),
        (4, False)
    ]
)
async def test_get_storage_server_from_job_id(init_job, repo, session, job_id, exist):
    """Test get a object."""
    if exist:
        exist_obj = await session.scalar(
            select(Job).filter(Job.id == job_id).options(selectinload(Job.storage_server)))
        obj = await repo.get_storage_server_from_job_id(exist_obj.id)
        assert obj
        assert exist_obj.storage_server.id == obj.id
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.get_storage_server_from_job_id(job_id)
