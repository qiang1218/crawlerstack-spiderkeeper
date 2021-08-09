"""
Test storage service.
"""
import asyncio
import functools

import pytest
from sqlalchemy import select, func

from crawlerstack_spiderkeeper.dao import TaskDAO, ServerDAO
from crawlerstack_spiderkeeper.db.models import Storage, Task
from crawlerstack_spiderkeeper.services import StorageService
from crawlerstack_spiderkeeper.services.utils import Kombu
from crawlerstack_spiderkeeper.signals import server_stop
from crawlerstack_spiderkeeper.utils import AppData, AppId
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper.utils.states import States


@pytest.fixture()
async def app_data(init_task, factory_with_session):
    """Fixture app data."""
    async with factory_with_session(TaskDAO) as dao:
        tasks = await dao.get(limit=1)
        task = tasks[0]
        job_id = task.job_id
        pk = task.id
    yield AppData(app_id=str(AppId(job_id, pk)), data={'foo': 'bar'})


@pytest.mark.asyncio
async def test_create(mocker, session_factory, app_data, factory_with_session):
    """Test create a storage."""
    async with factory_with_session(StorageService) as service:
        mocker.patch.object(service.kombu, 'publish')
        await service.create(app_data)
    async with session_factory() as session:
        task = await session.get(Task, app_data.app_id.task_id)
    assert task.item_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ['server', 'exporter_cls', 'except_value'],
    [
        (True, True, None),
        (True, False, 'is not support'),
        (False, False, 'not config server info.'),
        (False, True, 'not config server info.'),
    ]
)
async def test_exporter(mocker, init_job, server, factory_with_session, exporter_cls, except_value):
    """Test export error."""
    exporter_cls_mocker = mocker.MagicMock()
    mocker.patch.object(
        ServerDAO, 'get_server_by_job_id',
        return_value=mocker.MagicMock() if server else None
    )
    mocker.patch(
        'crawlerstack_spiderkeeper.services.storage.exporters_factory',
        return_value=exporter_cls_mocker if exporter_cls else exporter_cls
    )
    async with factory_with_session(StorageService) as service:

        if except_value:
            with pytest.raises(SpiderkeeperError):
                await service.exporter(1)
        else:
            await service.exporter(1)
            exporter_cls_mocker.from_url.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ['exception', 'state'],
    [
        (None, States.FINISH.value),
        (SpiderkeeperError('foo'), States.FAILURE.value),
    ]
)
async def test_consume_task(mocker, app_data, session, factory_with_session, caplog, exception, state):
    """Test consume task."""
    mocker.patch.object(
        Kombu,
        'consume',
        new_callable=mocker.AsyncMock,
        side_effect=exception
    )
    fut = asyncio.Future()
    async with factory_with_session(StorageService) as service:
        await service.consume_task(app_data.app_id, fut)
    stmt = select(func.count()).select_from(Storage)
    count = await session.scalar(stmt)
    assert count == 1
    storage_obj: Storage = await session.scalar(select(Storage))
    if exception:
        assert exception.args[0] in caplog.text

    assert storage_obj.state == state


@pytest.mark.asyncio
async def test__consuming_and_callback(mocker, init_storage, session, factory_with_session):
    """Test callback."""
    async with session.begin():
        storage = await session.scalar(select(Storage))
        pk = storage.id
        before = storage.count
    loop = asyncio.get_running_loop()
    callback = mocker.MagicMock()
    message = mocker.MagicMock()
    async with factory_with_session(StorageService) as service:
        _consuming_and_callback = functools.partial(
            service._consuming_and_callback,
            body={'foo': 'bar'},
            message=message,
            callback=callback,
            storage_id=pk,
            loop=asyncio.get_running_loop(),
        )
        await loop.run_in_executor(
            executor=None,
            func=_consuming_and_callback,
        )
        callback.assert_called_once()
    async with session.begin():
        obj = await session.get(Storage, pk)
        assert before + 1 == obj.count


@pytest.mark.asyncio
async def test_has_running_task(init_storage, session, app_data, factory_with_session):
    """Test has running task."""
    stmt = select(Storage).filter(Storage.state == States.RUNNING.value)
    async with session.begin():
        obj = await session.scalar(stmt)
        assert obj
        pk = obj.id
    async with factory_with_session(StorageService) as service:
        await service.has_running_task(app_data.app_id)
    async with session.begin():
        obj = await session.get(Storage, pk)
        assert obj.state == States.STOPPED.value


@pytest.mark.asyncio
async def test_start(mocker, app_data, factory_with_session):
    """Test start storage task."""
    async with factory_with_session(StorageService) as service:
        mocker.patch.object(service, 'consume_task', new_callable=mocker.AsyncMock)
        result = await service.start(app_data.app_id)
        assert result == 'Run storage task.'
        result = await service.start(app_data.app_id)
        assert result == 'Storage task already run.'
        result = await service.stop(app_data.app_id)
        assert result == 'Stopping storage task.'
        result = await service.stop(app_data.app_id)
        assert result == 'No storage task.'


@pytest.mark.asyncio
async def test_server_stop(mocker, app_data, factory_with_session):
    """Test server stop."""
    async with factory_with_session(StorageService) as service:
        mocker.patch.object(service, 'consume_task', new_callable=mocker.AsyncMock)
        await service.start(app_data.app_id)
        await server_stop.send()
    assert not service.storage_tasks
