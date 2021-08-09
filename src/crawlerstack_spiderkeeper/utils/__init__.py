"""
Utils
"""
import asyncio
import logging
import os
import signal
import socket
from asyncio import Future
from contextlib import contextmanager
from functools import partial, wraps
from pathlib import Path
from typing import (Any, AsyncIterable, Callable, Dict, List, Optional, Tuple,
                    TypeVar, Union)

import aiofiles
import psutil
from aiofiles.threadpool.binary import AsyncBufferedReader
from starlette.datastructures import UploadFile
from starlette.requests import Request

from crawlerstack_spiderkeeper.config import settings
from crawlerstack_spiderkeeper.utils.metadata import ArtifactMetadata

logger = logging.getLogger(__name__)


class SingletonMeta(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
        return cls.__instances[cls]


def get_db(request: Request):
    """
    从 Request 对象中获取已注入的 db 对象。
    :param request:
    :return:
    """
    return request.state.db


async def run_in_executor(func: Callable, *args, **kwargs) -> Any:
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
    """
    AppID 对象模型
    """
    prefix = 'APPID'
    separator = '-'

    def __init__(self, job_id: int, task_id: int):
        self.job_id = job_id
        self.task_id = task_id

    @classmethod
    def from_str(cls, app_id: str) -> 'AppId':
        """
        Get app id from str.
        :param app_id:
        :return:
        """
        _, job_id, task_id = app_id.split(cls.separator)
        return cls(job_id, task_id)

    def __eq__(self, other) -> bool:
        """eq"""
        if self.__repr__() == other.__repr__():
            return True
        return False

    def __repr__(self):
        """Return str fmt app id."""
        data = [self.prefix, self.job_id, self.task_id]
        return self.separator.join([str(x) for x in data])


class AppData:
    """
    AppData 对象
    """

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
    async with aiofiles.open(file_metadata.file, 'wb+') as f_obj:
        while True:
            data = await file.read(1024 * 1024 * 1024)
            if not data:
                break
            await f_obj.write(data)
    return file_metadata.filename


def get_host_addr():
    """
    获取主机地址。
    如果已在 settings 配置，则返回配置的主机地址，
    如果没有配置，则基于 socket 获取当前主机地址。
    :return:
    """
    host_addr = settings.HOST_ADDR
    return host_addr if host_addr else socket.gethostname()


MAX_PAGE_SIZE = 10


class CommonQueryParams:
    """
    通用 URL 查询参数
    """

    def __init__(
            self,
            start: int = 0,
            end: int = MAX_PAGE_SIZE,
            order: str = 'DESC',
            sort: str = 'id'
    ):
        start = max(start, 0)
        if end < start:
            end = start + MAX_PAGE_SIZE

        limit = end - start
        if limit > MAX_PAGE_SIZE or limit < 0:
            limit = MAX_PAGE_SIZE

        self.skip = start
        self.limit = limit
        self.order = order
        self.sort = sort


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
    for child_process in children:
        # TODO fix delay kill
        # 连发两次 ctrl-c 信号 ，像 scrapy 在发送两次才会强制结束。。
        # 参考 https://docs.scrapy.org/en/latest/_modules/scrapy/crawler.html#CrawlerProcess.start
        # 但这么做会造成处于队列中的数据丢失。
        # 如果发送一次 ctrl-c，会由于 scrapy 处理队列数据耗时太长，造成无法立即返回进程已结束的结果
        child_process.send_signal(sig)
        child_process.send_signal(sig)
    gone, alive = psutil.wait_procs(
        children,
        timeout=timeout,
        callback=on_terminate
    )
    logger.debug(
        'Try SIGTERM ppid: {pid}, alive: %s , gone: %s',
        [process.pid for process in alive],
        [process.pid for process in alive]
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
    """
    Tail 显示文件内容
    """

    def __init__(self, filename: str):
        self.filename = Path(filename)

    async def head(self, line_number: int = 50) -> AsyncIterable[str]:
        """
        获取文件钱几行
        :param line_number:
        :return:
        """
        line_count = 0
        async with aiofiles.open(self.filename, 'rb') as f_obj:
            async for line in f_obj:
                if line_count >= line_number:
                    break
                line_count += 1
                yield line.decode()

    async def last(self, line: int = 50, buffer_size=1024) -> AsyncIterable[str]:
        """
        通过 buffer_size 不断从文件最后往前查找所出现的 `\n` 行分隔符，统计出所需要行数位置，然后从该出读取文件。
        注意：行分隔符使用的是 `\n`
        :param line:
        :param buffer_size:
        :return:
        """

        async with aiofiles.open(self.filename, 'rb') as reader:
            # 判断文件大小是否大于最小缓冲大小
            # 如果大于，则根据缓冲区大小不断向前调整
            # 直到找到最后 n 行
            if self.filename.stat().st_size > abs(buffer_size):
                await forward_fd(reader, buffer_size, line)
            async for i in reader:
                yield i.decode()

    async def follow(
            self,
            block_size=512,
            stop: Optional[Future] = None,
    ) -> AsyncIterable[str]:
        """
        tail -f xxx.txt
        :param block_size:
        :param stop:
        :return:
        """
        async with aiofiles.open(self.filename, 'rb') as f_obj:

            if self.filename.stat().st_size > abs(block_size):
                await f_obj.seek(-block_size, os.SEEK_END)
            else:
                await f_obj.seek(0, os.SEEK_SET)

            while True:
                if stop and stop.done():
                    break
                where = await f_obj.tell()
                line = await f_obj.readline()
                if line:
                    yield line.decode()
                else:
                    await asyncio.sleep(1)
                    await f_obj.seek(where)


async def forward_fd(reader: AsyncBufferedReader, buffer_size: int, line: int):
    """
    调整文件读取对象的读取偏移量，从文件最后向前调整 line 行的偏移量
    :param reader:
    :param buffer_size:
    :param line:
    :return:
    """
    offset = buffer_size  # 调整的偏移量
    offset_times = 0  # 基于 buffer_size 调整的次数
    await reader.seek(0, os.SEEK_END)  # 调整到文件末尾
    offset_line = 0
    # 开始调整位置
    while True:
        await reader.seek(-offset, os.SEEK_CUR)  # 从当前位置向钱调整偏移量
        # 从调整位置读取所有内容，然后统计操作系统的换行符数量
        txt = await reader.read(offset)
        temp_offset_line = txt.count(os.linesep.encode('utf-8')) + offset_line

        if temp_offset_line >= line:
            # 如果统计行数大于所需要的行数
            if offset > buffer_size:
                # 如果 offset 大于 buffer_size ，则调整 offset 重新查找
                offset -= buffer_size
            else:
                await reader.seek(-offset, os.SEEK_CUR)
                break
        # 动态调整 buffer_size 大小，以加快速度查找速度
        else:
            offset_times += int(offset / buffer_size)
            offset_line = temp_offset_line
            await reader.seek(-offset, os.SEEK_CUR)

            if temp_offset_line < line / 2:
                # 当统计行数小于所需要行数的一半时
                # 每当进行 40 次调整时，将 buffer_size 增大一倍
                # 这么做可以更快速的向前调整
                if offset_times % 10 == 0:
                    offset += buffer_size
            else:
                if offset > buffer_size and offset_times % 10 == 0:
                    # 当统计行数大于所需要行数的一般时，
                    # 如果 offset 大于 buffer_size 则不断缩小范围
                    # 目的是获取更精确的行数，而不会和预期行数偏差太大
                    offset -= buffer_size
