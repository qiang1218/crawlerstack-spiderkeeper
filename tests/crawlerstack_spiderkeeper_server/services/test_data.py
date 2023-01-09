"""test data"""

import pytest

from crawlerstack_spiderkeeper_server.data_storage import MysqlStorage
from crawlerstack_spiderkeeper_server.services import DataService, TaskDetailService


@pytest.fixture()
def service():
    """service fixture"""
    return DataService()


@pytest.fixture()
def task_detail_service():
    """service fixture"""
    return TaskDetailService()


@pytest.mark.parametrize(
    'task_name, data',
    [
        ('test1', {'datas': [1, 2, 3], 'title': 'test_table', 'fields': ['column_1', 'column_2', 'column_3']}),

    ]
)
async def test_create(init_task, mocker, session, service, task_name, data):
    """test create"""
    start = mocker.patch.object(MysqlStorage, 'start', return_value=MysqlStorage())
    save = mocker.patch.object(MysqlStorage, 'save', return_value=True)
    create_or_update_task_detail = mocker.patch.object(DataService, 'create_or_update_task_detail')
    await service.create(task_name, data)
    start.assert_called_once()
    save.assert_called_once()
    create_or_update_task_detail.assert_called_once()


@pytest.mark.parametrize(
    'task_name, data_count, status',
    [
        ('test1', 2, True),

    ]
)
async def test_create_task_detail(init_task, session, service, task_detail_service, task_name, data_count, status):
    """test create task detail"""
    before_count = await task_detail_service.count()
    await service.create_or_update_task_detail(task_name, data_count, status)
    after_count = await task_detail_service.count()
    assert before_count == after_count - 1


@pytest.mark.parametrize(
    'pk, task_name, data_count, status',
    [
        (1, 'test1', 5, True),

    ]
)
async def test_update_task_detail(init_task_detail, session, service, task_detail_service, pk, task_name, data_count,
                                  status):
    """test update task detail"""
    before = await task_detail_service.get_by_id(pk)
    await service.create_or_update_task_detail(task_name, data_count, status)
    after = await task_detail_service.get_by_id(pk)
    assert before.item_count != after.item_count
    assert after.item_count == data_count
