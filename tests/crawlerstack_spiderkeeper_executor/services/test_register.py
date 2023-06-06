"""Test register"""
import pytest

from crawlerstack_spiderkeeper_executor.services import RegisterService
from crawlerstack_spiderkeeper_executor.utils.request import RequestWithHttpx


@pytest.fixture
def register_service(settings):
    """Register service fixture"""
    return RegisterService(settings)


async def test_register(register_service, mocker):
    """test register"""
    request = mocker.patch.object(RequestWithHttpx, 'request', return_value={'data': {'id': 1}})
    executor_id = await register_service.register()
    assert executor_id == 1
    request.assert_called_once()


# async def test_heartbeat_success(register_service, mocker):
#     """test heartbeat"""
#     request = mocker.patch.object(RequestWithSession, 'request', return_value={'message': 'ok'})
#     await register_service.heartbeat(executor_id=1)
#     await asyncio.sleep(7)
#     assert request.called
#     assert not register_service.exist
#
#
# async def test_heartbeat_failed(register_service, mocker):
#     """test heartbeat"""
#     request = mocker.patch.object(RequestWithSession, 'request', return_value={})
#     await register_service.heartbeat(executor_id=1)
#     await asyncio.sleep(7)
#     assert request.called
#     assert register_service.exist
