import asyncio
import os
from pathlib import Path
from subprocess import Popen

import pytest

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.utils import (AppId, ArtifactMetadata,
                                             CommonQueryParams, Tail,
                                             get_host_addr, kill_proc_tree,
                                             staging_path, upload)


def test_get_host_addr(monkeypatch):
    host_addr = get_host_addr()
    assert host_addr != "test"

    monkeypatch.setattr(settings, "HOST_ADDR", "test")
    host_addr = get_host_addr()
    assert host_addr == "test"


@pytest.mark.asyncio
async def test_upload(uploaded_file, temp_dir):
    metadata = ArtifactMetadata('xxx.demo')
    metadata.metadata.artifact_path = temp_dir
    await upload(uploaded_file, metadata)
    assert os.path.exists(metadata.file)


def test_common_query_params():
    params = CommonQueryParams(10, 10)
    assert params.size == 10
    assert params.page == 10


class TestAppId:

    def test_from_str(self):
        job_id, task_id = 1, 2
        app_id_str = f'{AppId.prefix}-{job_id}-{task_id}'
        app_id = AppId.from_str(app_id_str)
        assert str(app_id) == app_id_str

    def test(self):
        job_id, task_id = 1, 2
        app_id = AppId(job_id, task_id)
        assert str(app_id) == f'{app_id.prefix}-{job_id}-{task_id}'


def test_kill_proc_tree():
    process = Popen('sleep 5'.split())
    gone, alive = kill_proc_tree(process.pid)
    assert process.pid in [p.pid for p in gone]


def test_staging_path(temp_dir):
    with staging_path(temp_dir):
        assert os.getcwd() == temp_dir


@pytest.fixture()
def demo_file(test_data_dir) -> Path:
    yield Path(test_data_dir) / 'agpl-3.0.txt'


class TestTail:

    @pytest.fixture()
    def tail(self, demo_file):
        yield Tail(str(demo_file))

    @pytest.mark.asyncio
    async def test_head(self, tail):
        count = 0
        async for _ in tail.head(10):
            count += 1

        assert count == 10

    @pytest.mark.asyncio
    async def test_last(self, tail):
        count = 0

        async for _ in tail.last(3, 2):
            count += 1

        assert count >= 3

    @pytest.mark.parametrize(
        'block_size',
        [512, 128]
    )
    @pytest.mark.asyncio
    async def test_tail(self, tail, block_size):
        count = 0

        async def follow():
            nonlocal count
            async for _ in tail.follow(block_size):
                count += 1

        loop = asyncio.get_running_loop()
        task = loop.create_task(follow())
        await asyncio.sleep(0.1)
        task.cancel()
        assert count
