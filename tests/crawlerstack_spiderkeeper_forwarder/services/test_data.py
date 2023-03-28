"""Test data"""
import pytest

from crawlerstack_spiderkeeper_forwarder.forwarder.data import DataPublishTask
from crawlerstack_spiderkeeper_forwarder.schemas.data import DataSchema
from crawlerstack_spiderkeeper_forwarder.services import DataService


@pytest.fixture
def data_service():
    """Data task"""
    return DataService()


async def test_create(data_service, data, mocker):
    """Test create"""
    obj_in = DataSchema(**data)
    publish = mocker.patch.object(DataPublishTask, 'publish')
    await data_service.create(obj_in=obj_in)
    publish.assert_called_once()
