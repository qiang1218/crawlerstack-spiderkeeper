"""test log"""

import pytest

from crawlerstack_spiderkeeper_server.services import LogService


@pytest.fixture()
def service():
    """service fixture"""
    return LogService()


@pytest.mark.parametrize(
    'task_name, return_value',
    [
        ('2-scheduled-20191215152202', '2/scheduled/20191215152202'),
    ]
)
def test_gen_log_path_str(settings, service, task_name, return_value):
    """test get log path str"""
    log_path = service.gen_log_path_str(task_name)
    assert log_path.match(return_value + settings.LOG_TASK_PATH_SUFFIX)


@pytest.mark.parametrize(
    'task_name, rows',
    [
        ('', 5),
    ]
)
async def test_get(service, mocker, demo_file, task_name, rows):
    """test get"""
    gen_log_path_str = mocker.patch.object(LogService, 'gen_log_path_str', return_value=demo_file)
    result = await service.get({'task_name': task_name, 'rows': rows})
    assert len(result) == rows
    assert gen_log_path_str.called


@pytest.mark.parametrize(
    'task_name, rows',
    [
        ('', 5),
    ]
)
async def test_create(service, mocker, demo_create_file, task_name, rows):
    """test create"""
    gen_log_path_str = mocker.patch.object(LogService, 'gen_log_path_str', return_value=demo_create_file)
    result = await service.get({'task_name': task_name, 'rows': rows})
    before_count = len(result)
    await service.create({'data': ['test1', 'test2']})

    result = await service.get({'task_name': task_name, 'rows': rows})
    after_count = len(result)
    assert before_count == after_count - 2
    assert gen_log_path_str.called
