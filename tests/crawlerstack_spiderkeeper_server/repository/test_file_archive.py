"""test file archive"""
import pytest
from sqlalchemy import select

from crawlerstack_spiderkeeper_server.models import FileArchive
from crawlerstack_spiderkeeper_server.repository.file_archive import \
    FileArchiveRepository
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist


@pytest.fixture()
async def repo():
    """repo fixture"""
    return FileArchiveRepository()


@pytest.mark.parametrize(
    'name, exist',
    [
        ('test1', True),
        ('foo', False)
    ]
)
async def test_get_by_name(init_file_archive, repo, session, name, exist):
    """Test get a object."""
    if exist:
        exist_obj = await session.scalar(
            select(FileArchive).filter(FileArchive.name == name))
        obj = await repo.get_by_name(name)
        assert obj
        assert exist_obj.id == obj.id
    else:
        with pytest.raises(ObjectDoesNotExist):
            await repo.get_by_name(name)
