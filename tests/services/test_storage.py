"""
Test storage service.
"""
import asyncio
import functools
from pathlib import Path

import pytest
from furl import furl
from sqlalchemy import select, func

from crawlerstack_spiderkeeper.dao import TaskDAO, ServerDAO
from crawlerstack_spiderkeeper.db.models import Storage, Task, Server, Job
from crawlerstack_spiderkeeper.services import StorageService
from crawlerstack_spiderkeeper.services.storage import StorageBackgroundTask
from crawlerstack_spiderkeeper.services.utils import Kombu
from crawlerstack_spiderkeeper.utils import AppData, AppId
from crawlerstack_spiderkeeper.utils.exceptions import SpiderkeeperError
from crawlerstack_spiderkeeper.utils.status import Status


@pytest.fixture()
async def app_data(init_task, factory_with_session):
    """Fixture app data."""
    async with factory_with_session(TaskDAO) as dao:
        tasks = await dao.get(limit=1)
        task = tasks[0]
        job_id = task.job_id
        pk = task.id
    yield AppData(app_id=str(AppId(job_id, pk)), data={'foo': 'bar'})


class TestStorageBackgroundTask:

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
    async def test_exporter(self, mocker, init_job, server, app_data, session, exporter_cls, except_value):
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
        should_stop = asyncio.Future()
        task = StorageBackgroundTask(app_data.app_id, session, should_stop)

        if except_value:
            with pytest.raises(SpiderkeeperError):
                await task.exporter()
        else:
            await task.exporter()
            exporter_cls_mocker.from_url.assert_called_once()

    @pytest.mark.asyncio
    async def test__consuming_and_callback(self, mocker, init_storage, app_data, session, factory_with_session):
        """Test callback."""
        async with session.begin():
            storage = await session.scalar(select(Storage))
            pk = storage.id
            before = storage.count
        loop = asyncio.get_running_loop()
        callback = mocker.MagicMock()
        message = mocker.MagicMock()

        task = StorageBackgroundTask(app_data.app_id, session, asyncio.Future())
        _consuming_and_callback = functools.partial(
            task._consuming_and_callback,
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
    @pytest.mark.parametrize(
        ['exception', 'status'],
        [
            (None, Status.FINISH.value),
            (SpiderkeeperError('foo'), Status.FAILURE.value),
        ]
    )
    async def test_consume_task(self, mocker, app_data, session, caplog, exception, status):
        """Test consume task."""
        mocker.patch.object(
            Kombu,
            'consume',
            new_callable=mocker.AsyncMock,
            side_effect=exception
        )
        task = StorageBackgroundTask(app_data.app_id, session, asyncio.Future())
        await task.consume_task()
        stmt = select(func.count()).select_from(Storage)
        count = await session.scalar(stmt)
        assert count == 1
        storage_obj: Storage = await session.scalar(select(Storage))
        if exception:
            assert exception.args[0] in caplog.text

        assert storage_obj.status == status

    @pytest.mark.asyncio
    async def test_run(self, mocker, app_data, event_loop, session):
        fut = asyncio.Future()
        task = event_loop.create_task(StorageBackgroundTask.run_from_cls(app_id=app_data.app_id, should_stop=fut))
        await asyncio.sleep(0.1)
        fut.set_result('Finish')
        await asyncio.sleep(1)
        assert task.done()
        count = await session.scalar(select(func.count()).select_from(Storage))
        assert count == 1
        storage = await session.get(Storage, 1)
        assert storage.status == Status.FINISH.value


class TestStorageService:

    @pytest.mark.parametrize(
        'times',
        [1, 2]
    )
    @pytest.mark.asyncio
    async def test_create(self, mocker, session_factory, app_data, factory_with_session, times):
        """Test create a storage."""
        async with factory_with_session(StorageService) as service:
            mocker.patch.object(service.kombu, 'publish')
            await service.create(app_data)
        async with session_factory() as session:
            task = await session.get(Task, app_data.app_id.task_id)
        assert task.item_count == 1

    @pytest.mark.asyncio
    async def test_has_running_task(self, init_storage, session, app_data, factory_with_session):
        """Test has running task."""
        stmt = select(Storage).filter(Storage.status == Status.RUNNING.value)
        async with session.begin():
            obj = await session.scalar(stmt)
            assert obj
            pk = obj.id

        async with factory_with_session(StorageService) as service:
            await service.is_running(app_data.app_id)
        async with session.begin():
            # 使用 populate_existing=True 显示指定从数据库查询，并刷新对象。
            # 这么做的目的是避免前面查询后中间其他连接修改了，再次查询直接读缓存的情况。
            obj = await session.get(Storage, pk, populate_existing=True)
            assert obj.status == Status.STOPPED.value

    @pytest.mark.asyncio
    async def test_start(self, mocker, app_data, factory_with_session):
        """Test start storage task."""

        async def mock_method(app_id, should_stop, session=None):
            """"""
            await should_stop

        mock_task = mocker.patch('crawlerstack_spiderkeeper.services.storage.StorageBackgroundTask')
        mock_task.run_from_cls = mock_method

        async with factory_with_session(StorageService) as service:
            result = await service.start(app_data.app_id)
            assert result == 'Run storage task.'
            result = await service.start(app_data.app_id)
            assert result == 'Storage task already run.'
            result = await service.stop(app_data.app_id)
            assert result == 'Stopping storage task.'
            result = await service.stop(app_data.app_id)
            assert result == 'No storage task.'

    @pytest.mark.parametrize(
        'a',
        [1, 2]
    )
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_start_stop_task(self, mocker, app_data, init_job, session, factory_with_session, a):
        """"""
        event_loop = asyncio.get_running_loop()
        mock_exporter = mocker.MagicMock()
        mocker.patch.object(StorageBackgroundTask, 'exporter', return_value=mock_exporter)
        mock_write = mocker.MagicMock()
        mock_exporter.write = mock_write
        async with factory_with_session(StorageService) as service:
            await service.create(app_data)
            res = await service.start(app_data.app_id)
            assert 'Run storage task.' == res
            await asyncio.sleep(0.1)
            res = await service.stop(app_data.app_id)
            await asyncio.sleep(1)
            print('test event_loop status:', id(event_loop), event_loop.is_running())
            mock_write.assert_called_once_with(app_data.data)
