import time

import pytest

from crawlerstack_spiderkeeper_server.utils import File
import crawlerstack_spiderkeeper_server


@pytest.fixture()
def tail(demo_file):
    """Fixture tail"""
    yield File(demo_file)


@pytest.mark.parametrize(
    'lines, block_size,',
    [
        (10, 5),
    ]
)
async def test_last(tail, lines, block_size):
    """Test last line."""
    data = await tail.last(10)
    assert len(data) == lines


async def test_head(tail):
    """Test head line."""
    count = 0
    async for _ in tail.head(10):
        count += 1
    assert count == 10


@pytest.mark.parametrize(
    ['block_size', 'expect_value'],
    [
        (2048, 22),
        (100, 4),
    ]
)
async def test_tail(tail, event_loop, mocker, block_size, expect_value):
    """Test tail."""
    mocker.patch.object(
        crawlerstack_spiderkeeper_server.utils.asyncio,
        'sleep',
        new_callable=mocker.AsyncMock
    )

    async def follow(fut):
        """tail -f log task."""
        _count = 0
        async for _ in tail.follow(block_size, fut):
            _count += 1
        return _count

    def write_log(filename):
        """a writer log mocker"""
        time.sleep(0.1)
        with open(filename, 'a', encoding='utf-8') as file:
            file.write('hello \n')
            file.flush()
        time.sleep(0.1)

    stop = event_loop.create_future()  # noqa
    task = event_loop.create_task(follow(stop))  # noqa
    await event_loop.run_in_executor(None, write_log, tail.filename)  # noqa
    stop.set_result('stop')
    count = await task
    assert count == expect_value
