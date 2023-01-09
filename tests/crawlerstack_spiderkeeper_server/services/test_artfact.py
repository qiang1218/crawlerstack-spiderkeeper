"""test artifact"""
import pytest

from crawlerstack_spiderkeeper_server.services.artifact import ArtifactService
from crawlerstack_spiderkeeper_server.schemas.artifact import ArtifactCreate, ArtifactUpdate
from crawlerstack_spiderkeeper_server.utils.exceptions import ObjectDoesNotExist


@pytest.fixture()
def service():
    """service fixture"""
    return ArtifactService()


@pytest.mark.parametrize(
    'project_id, exist',
    [
        (1, True),
        (100, False)
    ]
)
async def test_create(init_project, session, service, project_id, exist):
    """test create"""
    obj_in = ArtifactCreate(name="test1", desc="test1", image='test1', version='latest', project_id=project_id)
    if exist:
        await service.create(obj_in=obj_in)
        count = await service.count()
        assert count == 1
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.create(obj_in=obj_in)


@pytest.mark.parametrize(
    'pk, exist',
    [
        (1, True),
        (100, False)
    ]
)
async def test_update_by_id(init_artifact, session, service, pk, exist):
    """test update by id"""
    obj_in = ArtifactUpdate(desc='change_test_01')
    if exist:
        before = await service.get_by_id(pk)
        await service.update_by_id(pk, obj_in=obj_in)
        after = await service.get_by_id(pk)
        assert before
        assert after.desc != before.desc
        assert after.desc == obj_in.desc
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.update_by_id(pk, obj_in=obj_in)


@pytest.mark.parametrize(
    'pk, exist',
    [
        (1, True),
        (100, False)
    ]
)
async def test_get_project_from_artifact_id(init_artifact, session, service, pk, exist):
    """test get project from artifact"""
    if exist:
        result = await service.get_project_from_artifact_id(pk)
        assert result
        assert result.name == "test1"
    else:
        with pytest.raises(ObjectDoesNotExist):
            await service.get_project_from_artifact_id(pk)
