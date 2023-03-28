"""test file archive"""
import pytest

from crawlerstack_spiderkeeper_server.services.file_archive import \
    FileArchiveService
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist


@pytest.fixture()
def service():
    """service fixture"""
    return FileArchiveService()


@pytest.mark.parametrize(
    'name, exist',
    [
        ('test1', True),
        ('foo', False)
    ]
)
async def test_get_by_name(init_file_archive, session, service, name, exist):
    """test get project from artifact"""
    if exist:
        result = await service.get_by_name(name)
        assert result
        assert result.name == name
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.get_by_name(name)
