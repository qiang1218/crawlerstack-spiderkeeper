"""
Test storage service.
"""
# import asyncio
#
# import pytest
# from kombu import Message
#
# from crawlerstack_spiderkeeper.dao import TaskDAO
# from crawlerstack_spiderkeeper.db.models import Storage, Task
# from crawlerstack_spiderkeeper.services import storage_service, StorageService
# from crawlerstack_spiderkeeper.signals import server_stop
# from crawlerstack_spiderkeeper.utils import AppData, AppId
# from crawlerstack_spiderkeeper.utils.states import States
#
#
# @pytest.fixture()
# async def app_data(init_task, factory_with_session):
#     """Fixture app data."""
#     async with factory_with_session(TaskDAO) as dao:
#         tasks = await dao.get(limit=1)
#         task = tasks[0]
#     yield AppData(app_id=str(AppId(task.job_id, task.id)), data={'foo': 'bar'})
#
#
# @pytest.mark.asyncio
# async def test_create(mocker, init_task, session, app_data, factory_with_session):
#     """Test create a storage."""
#     async with factory_with_session(StorageService) as service:
#         mocker.patch.object(service, 'publish')
#         await service.create(app_data)
#     task = await session.get(Task, app_data.app_id.task_id)
#     assert task.item_count == 1
#
#
# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     ['server', 'exporter_cls', 'except_value'],
#     [
#         (True, True, None),
#         (True, False, 'is not support'),
#         (False, False, 'not config server info.'),
#         (False, True, 'not config server info.'),
#     ]
# )
# async def test__exporter_error(mocker, server, exporter_cls, except_value):
#     """Test export error."""
#     mocker.patch(
#         'crawlerstack_spiderkeeper.services.storage.run_in_executor',
#         new_callable=mocker.AsyncMock,
#         return_value=mocker.MagicMock() if server else server
#     )
#     exporter_cls_mocker = mocker.MagicMock()
#     mocker.patch(
#         'crawlerstack_spiderkeeper.services.storage.exporters_factory',
#         return_value=exporter_cls_mocker if exporter_cls else exporter_cls
#     )
#     if except_value:
#         with pytest.raises(Exception, match=except_value):
#             await storage_service._exporter(1)  # pylint: disable=protected-access
#     else:
#         await storage_service._exporter(1)  # pylint: disable=protected-access
#         exporter_cls_mocker.from_url.assert_called_once()
#
#
# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     ['exception', 'state'],
#     [
#         (None, States.FINISH.value),
#         (Exception('foo'), States.FAILURE.value)
#     ]
# )
# async def test_consume_task(mocker, app_data, session, caplog, exception, state):
#     """Test consume task."""
#     mocker.patch.object(
#         storage_service,
#         'consume',
#         new_callable=mocker.AsyncMock,
#         side_effect=exception
#     )
#     fut = asyncio.Future()
#     await storage_service.consume_task(app_data.app_id, fut)
#     assert session.query(Storage).count() == 1
#     storage_obj: Storage = session.query(Storage).first()
#     if exception:
#         assert exception.args[0] in caplog.text
#
#     assert storage_obj.state == state
#
#
# @pytest.mark.parametrize('exception', [None, Exception()])
# def test_callback(mocker, init_storage, session, exception):
#     """Test callback."""
#     obj: Storage = session.query(Storage).first()
#     count = obj.count
#     storage_service.callback(
#         mocker.MagicMock(side_effect=exception),
#         obj.id,
#         {'foo': 'bar'},
#         mocker.MagicMock(new_callable=Message)
#     )
#     session.refresh(obj)
#     if exception:
#         assert obj.count == count
#     else:
#         assert obj.count == count + 1
#
#
# @pytest.mark.asyncio
# async def test_has_running_task(init_storage, session, app_data):
#     """Test has running task."""
#     obj = session.query(Storage).filter(Storage.state == States.RUNNING.value).first()
#     assert obj
#     await storage_service.has_running_task(app_data.app_id)
#     session.refresh(obj)
#     assert obj.state == States.STOPPED.value
#
#
# @pytest.mark.asyncio
# async def test_start(mocker, app_data):
#     """Test start storage task."""
#     mocker.patch.object(storage_service, 'consume_task', new_callable=mocker.AsyncMock)
#     result = await storage_service.start(app_data.app_id)
#     assert result == 'Run storage task.'
#     result = await storage_service.start(app_data.app_id)
#     assert result == 'Storage task already run.'
#     result = await storage_service.stop(app_data.app_id)
#     assert result == 'Stopping storage task.'
#     result = await storage_service.stop(app_data.app_id)
#     assert result == 'No storage task.'
#
#
# @pytest.mark.asyncio
# async def test_server_stop(mocker, app_data, signal_send):
#     """Test server stop."""
#     mocker.patch.object(storage_service, 'consume_task', new_callable=mocker.AsyncMock)
#     await storage_service.start(app_data.app_id)
#     await signal_send(server_stop)
#     assert not storage_service.storage_tasks
