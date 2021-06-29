"""
Test utils.
"""
import os
import tempfile
import time
from subprocess import Popen

import pytest

import crawlerstack_spiderkeeper
from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.utils import (AppData, AppId, ArtifactMetadata,
                                             CommonQueryParams, Tail,
                                             get_host_addr, kill_proc_tree,
                                             run_in_executor, staging_path,
                                             upload)
from crawlerstack_spiderkeeper.utils.mock import AsyncMock


@pytest.fixture()
def demo_file(temp_dir):
    """Fixture demo file"""
    with tempfile.NamedTemporaryFile(
            prefix='test-tail',
            suffix='.txt',
            dir=temp_dir
    ) as file:
        file.write("""MIT License

Copyright (c) <YEAR> <COPYRIGHT HOLDER>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""".encode())
        file.flush()
        yield file.name


@pytest.fixture()
def tail(demo_file):
    """Fixture tail"""
    yield Tail(str(demo_file))


@pytest.mark.asyncio
async def test_run_in_executor():
    """test run_in_executor"""

    def func():
        return True

    res = await run_in_executor(func)
    assert res


@pytest.mark.parametrize(
    'app_id, expect_value',
    [
        ('APPID-1-1', AppId(1, 1)),
        (AppId(1, 2), AppId(1, 2))
    ]
)
def test_app_data(app_id, expect_value):
    """test AppData"""
    app_data = AppData(app_id, {})
    assert app_data.app_id == expect_value


@pytest.mark.parametrize(
    'start, end, order, sort, expect_value',
    [
        (None, None, None, None, [0, 10, 'DESC', 'id']),
        (None, 100, None, None, [0, 10, 'DESC', 'id']),
        (90, None, None, None, [90, 10, 'DESC', 'id']),
        (90, 100, None, None, [90, 10, 'DESC', 'id']),
        (50, 100, None, None, [50, 10, 'DESC', 'id']),
    ]
)
def test_common_query_params(start, end, order, sort, expect_value):
    """test CommonQueryParams"""
    kwargs = {
        'start': start,
        'end': end,
        'order': order,
        'sort': sort
    }
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    params = CommonQueryParams(**kwargs)
    assert [params.skip, params.limit, params.order, params.sort] == expect_value


def test_get_host_address(monkeypatch):
    """Test get host address."""
    host_address = get_host_addr()
    assert host_address != "test"

    monkeypatch.setattr(settings, "HOST_ADDR", "test")
    host_address = get_host_addr()
    assert host_address == "test"


@pytest.mark.asyncio
async def test_upload(uploaded_file, temp_dir):
    """Test upload file."""
    metadata = ArtifactMetadata('xxx.demo')
    metadata.metadata.artifact_path = temp_dir
    await upload(uploaded_file, metadata)
    assert os.path.exists(metadata.file)


def test_init_app_id_from_str():
    """Test init AppId from str."""
    job_id, task_id = 1, 2
    app_id_str = f'{AppId.prefix}-{job_id}-{task_id}'
    app_id = AppId.from_str(app_id_str)
    assert str(app_id) == app_id_str


def test_init_app_id():
    """Test init AppId"""
    job_id, task_id = 1, 2
    app_id = AppId(job_id, task_id)
    assert str(app_id) == f'{app_id.prefix}-{job_id}-{task_id}'


def test_app_id_eq():
    """test app_id_qe"""
    assert AppId(1, 2) == AppId(1, 2)
    assert AppId(1, 2) != AppId(1, 1)


def test_kill_proc_tree():
    """Test kill process tree."""
    with Popen('sleep 5'.split()) as process:
        gone, _ = kill_proc_tree(process.pid)
        assert process.pid in [p.pid for p in gone]


def test_staging_path(temp_dir):
    """Test staging path."""
    with staging_path(temp_dir):
        assert os.getcwd() == temp_dir


@pytest.mark.asyncio
async def test_head(tail):
    """Test head line."""
    count = 0
    async for _ in tail.head(10):
        count += 1

    assert count == 10


@pytest.mark.asyncio
async def test_last(tail):
    """Test last line."""
    count = 0

    async for _ in tail.last(15, 5):
        count += 1

    assert count >= 5


@pytest.mark.parametrize(
    ['block_size', 'expect_value'],
    [
        (2048, 22),
        (100, 4),
    ]
)
@pytest.mark.asyncio
async def test_tail(tail, event_loop, mocker, block_size, expect_value):
    """Test tail."""
    mocker.patch.object(
        crawlerstack_spiderkeeper.utils.asyncio,
        'sleep',
        new_callable=AsyncMock
    )

    async def follow(fut):
        """tail -f log task."""
        _count = 0
        async for _ in tail.follow(block_size, fut):
            # print(_, end='')
            _count += 1
        return _count

    def write_log(filename):
        """a writer log mocker"""
        time.sleep(0.1)
        with open(filename, 'a', encoding='utf-8') as file:
            file.write('hello \n')
            file.flush()
        time.sleep(0.1)

    stop = event_loop.create_future()
    task = event_loop.create_task(follow(stop))
    await event_loop.run_in_executor(None, write_log, tail.filename)
    stop.set_result('stop')
    count = await task
    assert count == expect_value
