import asyncio
import logging
import os
import signal
import socket
from contextlib import contextmanager
from functools import partial, wraps
from pathlib import Path
from typing import (Any, AsyncIterable, Callable, Dict, List, Tuple, TypeVar,
                    Union)

import aiofiles
import psutil
from starlette.datastructures import UploadFile
from starlette.requests import Request

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.db import ScopedSession
from crawlerstack_spiderkeeper.utils.metadata import ArtifactMetadata

logger = logging.getLogger(__name__)


def get_db(request: Request):
    return request.state.db


async def run_in_executor(func, *args, **kwargs) -> Any:
    """
    如果自定义 executor 请在 kwargs 中传入。
    :param func:
    :param kwargs:
        : kwargs func 的字典参数
        : executor 自定义 executor
    :return:
    """
    executor = kwargs.pop('executor', None)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, partial(func, *args, **kwargs))


UploadFileType = TypeVar('UploadFileType', bound=UploadFile)


class AppId:
    prefix = 'APPID'
    separator = '-'

    def __init__(self, job_id: int, task_id: int):
        self.job_id = job_id
        self.task_id = task_id

    @classmethod
    def from_str(cls, app_id: str) -> 'AppId':
        _, job_id, task_id = app_id.split(cls.separator)
        return cls(job_id, task_id)

    def __repr__(self):
        data = [self.prefix, self.job_id, self.task_id]
        return self.separator.join(map(lambda x: str(x), data))


class AppData:

    def __init__(self, app_id: Union[str, AppId], data: Dict):
        self.app_id: AppId = app_id
        if isinstance(app_id, str):
            self.app_id: AppId = AppId.from_str(app_id)

        self.data: Dict = data


async def upload(file: UploadFileType, file_metadata: ArtifactMetadata) -> str:
    """

    :param file:    file obj
    :param file_metadata:
    :return:    filename
    """
    async with aiofiles.open(file_metadata.file, 'wb+') as f:
        while True:
            data = await file.read(1024 * 1024 * 1024)
            if not data:
                break
            await f.write(data)
    return file_metadata.filename


def get_host_addr():
    host_addr = settings.HOST_ADDR
    return host_addr if host_addr else socket.gethostname()


MAX_PAGE_SIZE = 10


class CommonQueryParams:
    def __init__(
            self,
            _start: int = 0,
            _end: int = 100,
            _order: str = 'DESC',
            _sort: str = 'id'
    ):
        if _start < 0:
            _start = 0
        if _end < _start:
            _end = _start + MAX_PAGE_SIZE

        limit = _end - _start
        if limit > MAX_PAGE_SIZE or limit < 0:
            limit = MAX_PAGE_SIZE

        self.skip = _start
        self.limit = limit
        self.order = _order
        self.sort = _sort


def kill_proc_tree(
        pid: int,
        sig=signal.SIGTERM,
        include_parent=True,
        timeout=None,
        on_terminate=None
) -> Tuple[List[psutil.Process], List[psutil.Process]]:
    """
    Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates.
    :param pid:
    :param sig:
    :param include_parent:
    :param timeout:
    :param on_terminate:    sync callback
    :return:
    """
    assert pid != os.getpid(), "won't kill myself"
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        # TODO fix delay kill
        # 连发两次 ctrl-c 信号 ，像 scrapy 在发送两次才会强制结束。。
        # 参考 https://docs.scrapy.org/en/latest/_modules/scrapy/crawler.html#CrawlerProcess.start
        # 但这么做会造成处于队列中的数据丢失。
        # 如果发送一次 ctrl-c，会由于 scrapy 处理队列数据耗时太长，造成无法立即返回进程已结束的结果
        p.send_signal(sig)
        p.send_signal(sig)
    gone, alive = psutil.wait_procs(
        children,
        timeout=timeout,
        callback=on_terminate
    )
    logger.debug(
        f'Try SIGTERM ppid: {pid}, '
        f'alive: {[process.pid for process in alive]} , '
        f'gone: {[process.pid for process in alive]}'
    )
    return gone, alive


@contextmanager
def staging_path(to_path):
    """
    # TODO 修改方法名
    暂时切换目录，执行完后返回之前目录
    :param to_path:
    :return:
    """
    cwd = os.getcwd()
    os.chdir(to_path)
    yield
    os.chdir(cwd)


class Tail:
    def __init__(self, filename: str):
        self.filename = Path(filename)

    async def head(self, line_number: int = 50) -> AsyncIterable[str]:
        line_count = 0
        async with aiofiles.open(self.filename, 'rb') as f:
            async for line in f:
                if line_count >= line_number:
                    break
                line_count += 1
                yield line.decode()

    async def last(self, line: int = 50, min_block_size=1024) -> AsyncIterable[str]:
        """
        通过 block_size 不断从文件最后往前查找所出现的 `\n` 行分隔符，统计出所需要行数位置，然后从该出读取文件。
        注意：行分隔符使用的是 `\n`
        :param line:
        :param min_block_size:
        :return:
        """
        async with aiofiles.open(self.filename, 'rb') as f:
            if self.filename.stat().st_size > abs(min_block_size):
                block_size = min_block_size
                block_number = 0
                await f.seek(0, os.SEEK_END)
                while True:
                    block_number += 1
                    await f.seek(-min_block_size * block_number, os.SEEK_END)
                    txt = await f.read()
                    line_count = txt.count(b'\n')

                    if line_count < line / 2:
                        # 当统计行数小于所需要行数的一般是
                        # 每当进行 40 的倍数次调整时，将 block_size 增大 min_block_size
                        # 这么做可以更快速的向前调整
                        if block_number % 40 == 0:
                            block_size += min_block_size
                    # 当统计行数大于所需要行数的一般时，
                    # 如果 block_size 大于 min_block_size 则不断缩小范围
                    # 目的是获取更精确的行数，而不会和预期行数偏差太大
                    elif block_size > min_block_size:
                        block_size -= min_block_size

                    # 如果统计行数大于所需要的行数，跳出循环。
                    if line_count >= line:
                        break
                await f.seek(-block_size * block_number, os.SEEK_END)
            async for i in f:
                yield i.decode()

    async def follow(self, block_size=512) -> AsyncIterable[str]:
        """
        tail -f xxx.txt
        :param block_size:
        :return:
        """
        async with aiofiles.open(self.filename, 'rb') as f:

            if self.filename.stat().st_size > abs(block_size):
                await f.seek(-block_size, os.SEEK_END)
            else:
                await f.seek(0, os.SEEK_SET)

            x = await f.tell()
            print(x)
            while True:
                where = await f.tell()
                line = await f.readline()
                if not line:
                    await asyncio.sleep(1)
                    await f.seek(where)
                else:
                    yield line.decode()


def scoping_session(func: Callable):
    @wraps(func)
    def __wrapper(*args, **kwargs):
        ScopedSession()
        try:
            return func(*args, **kwargs)
        finally:
            ScopedSession.remove()

    return __wrapper
