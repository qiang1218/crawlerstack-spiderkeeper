"""
Test customs sub
"""
import asyncio
import os
import shutil

import aiofiles
import pytest

from crawlerstack_spiderkeeper.executor.subprocess import (
    FileHandle, RotatingFileHandler, create_subprocess_shell)
from crawlerstack_spiderkeeper.utils.mock import AsyncMock


@pytest.fixture()
def log_dir(temp_dir):
    """Fixture log dir"""
    path = os.path.join(temp_dir, 'test_rotating_handler')
    os.makedirs(path, exist_ok=True)
    yield path
    shutil.rmtree(path)


@pytest.fixture()
def create_subprocess_shell_log_dir(temp_dir, log_dir):
    """Fixture subprocess shell log dir."""
    path = os.path.join(temp_dir, 'create_subprocess_shell')
    os.makedirs(path)
    yield log_dir
    shutil.rmtree(path)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('side_effect',),
    [
        (None,),
        (Exception('foo'),)
    ]
)
async def test_file_handle_write(mocker, event_loop, side_effect):
    """Test write"""
    writer_mocker = AsyncMock()
    writer_mocker.write = AsyncMock(side_effect=side_effect)
    open_mocker = mocker.patch.object(
        aiofiles,
        'open',
        return_value=writer_mocker,
        new_callable=AsyncMock
    )
    handler = FileHandle('foo.txt', event_loop)
    await handler.open()
    if side_effect:
        with pytest.raises(Exception):
            await handler.write(b'xxx')
    else:
        await handler.write(b'xxx')
        await handler.close()
    assert open_mocker.called
    assert writer_mocker.write.called
    assert writer_mocker.close.called


@pytest.mark.asyncio
async def test_rotating_file_handle_write(log_dir, count_file_factory):
    """Test rotating file handle write."""
    data = [
        '1' * 50,
        '2' * 50,
    ]
    filename = os.path.join(log_dir, 'test_rotating_handler.log')
    with open(filename + '.2', 'w') as f_obj:
        f_obj.write('foo')
    back_count = 3
    handler = RotatingFileHandler(filename, 100, back_count)
    for i in data:
        await handler.write(f'{i}\n'.encode())
    assert count_file_factory(log_dir) == back_count


@pytest.mark.asyncio
async def test_create_subprocess_shell(create_subprocess_shell_log_dir, count_file_factory):
    """Test create subprocess shell"""
    back_count = 2
    process = await create_subprocess_shell(
        cmd='echo "12345678" && echo "abc"',
        std_path=create_subprocess_shell_log_dir,
        max_bytes=10,
        back_count=back_count,
    )
    await process.wait()
    await asyncio.sleep(0.05)  # wait stdout and stderr write to file .
    assert count_file_factory(create_subprocess_shell_log_dir) == back_count
