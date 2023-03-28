"""
Customs subprocess
"""
import asyncio
import os
from asyncio import AbstractEventLoop, StreamReader, SubprocessTransport
from asyncio.subprocess import Process, SubprocessStreamProtocol
from pathlib import Path
from typing import Optional, Union

import aiofiles
from aiofiles.os import remove, rename
from aiofiles.threadpool.binary import AsyncFileIO


class FileHandle:
    """
    File handler
    """

    def __init__(
            self,
            filename: str,
            loop: Optional[AbstractEventLoop] = None
    ):
        self.filename = filename
        self._loop = loop or asyncio.get_running_loop()

        self.writer: Optional[AsyncFileIO] = None

        self.closing = False

    async def open(self) -> None:
        """
        Open file
        :return:
        """
        self.writer = await aiofiles.open(
            file=self.filename,
            mode='ab',
            loop=self._loop
        )

    async def write(self, line: bytes) -> None:
        """
        写入后就将缓存数据刷新到文件中，避免关闭文件时，其他写入对象还没来得及将内容写入。
        例如 stdout 和 stderr 同时写入一个文件是，如果不及时刷新，会出现日志积块的情况。
        或者当 stdout 备份了该文件， stderr 无法写入。
        :param line:
        :return:
        """
        try:
            await self.writer.write(line)
            await self.writer.flush()
        except Exception as ex:
            await self.close()
            raise ex

    async def close(self) -> None:
        """Close file"""
        self.closing = True
        if self.writer is not None:
            await self.writer.close()


class RotatingFileHandler(FileHandle):
    """
    Rota file handler
    """

    def __init__(
            self,
            filename: Union[str, Path],
            max_bytes: Optional[int] = 0,
            backup_count: Optional[int] = 0,
            loop: Optional[AbstractEventLoop] = None
    ):
        super().__init__(filename, loop)

        self.back_count = backup_count
        self.max_bytes = max_bytes

    async def write(self, line: bytes) -> None:
        """
        Write line.

        :param line:
        :return:
        """
        should_rollover = await self.should_rollover(line)
        if should_rollover:
            await self.do_rollover()
        await super().write(line)

    async def should_rollover(self, line: bytes) -> bool:
        """
        Check if rollover file
        :param line:
        :return:
        """
        if self.writer is None and not self.closing:
            await self.open()
        if self.max_bytes > 0:
            await self.writer.seek(0, os.SEEK_END)
            where = await self.writer.tell()
            if where + len(line) >= self.max_bytes:
                return True
        return False

    async def do_rollover(self) -> None:
        """
        Rollover file
        :return:
        """
        if self.writer:
            await self.writer.close()
            self.writer = None

        if self.back_count > 0:
            for i in range(self.back_count - 1, 0, -1):
                source_filename = f'{self.filename}.{i}'
                dest_filename = f'{self.filename}.{i + 1}'

                # 删除目标文件，然后将源文件重命名为目标文件
                # foo.log.5 -> foo.log.6
                # 先删除 foo.log.6，然后将 foo.log.5 改名为 foo.log.6
                if os.path.exists(source_filename):
                    if os.path.exists(dest_filename):
                        await remove(dest_filename)
                    await rename(source_filename, dest_filename)

            # 删除 foo.log.1 文件，然后将 foo.log 重命名为 foo.log.1
            dest_filename = f'{self.filename}.1'
            if os.path.exists(dest_filename):
                await remove(dest_filename)
            if os.path.exists(self.filename):
                await rename(self.filename, dest_filename)

        if not self.closing:
            await self.open()


class SubprocessRotatingFileProtocol(SubprocessStreamProtocol):
    """
    Subprocess rota file protocol
    """

    def __init__(
            self,
            limit: int,
            std_path: str,
            max_bytes: Optional[int] = 0,
            back_count: Optional[int] = 0,
            loop: Optional[AbstractEventLoop] = None,
    ):
        super().__init__(limit, loop)
        self._loop = loop or asyncio.get_running_loop()
        self.std_path = std_path

        self.max_bytes = max_bytes
        self.back_count = back_count

        self.stdout_handler: Optional[FileHandle] = None
        self.stderr_handler: Optional[FileHandle] = None

        self._closing_task: asyncio.Future = loop.create_future()

    def connection_made(self, transport: SubprocessTransport) -> None:
        """
        stderr 和 stdout 都写入到一个文件中。
        :param transport:
        :return:
        """
        super().connection_made(transport)
        pid = transport.get_pid()
        filename = f'pid-{pid}.log'

        self.stdout_handler = RotatingFileHandler(
            Path(self.std_path) / filename,
            self.max_bytes,
            self.back_count,
            loop=self._loop
        )
        self.stderr_handler = RotatingFileHandler(
            Path(self.std_path) / filename,
            self.max_bytes,
            self.back_count,
            loop=self._loop
        )

        self._loop.create_task(transform(self.stdout, self.stdout_handler))
        self._loop.create_task(transform(self.stderr, self.stderr_handler))


async def transform(reader: StreamReader, handler: 'RotatingFileHandler'):
    """
    transform
    :param reader:
    :param handler:
    :return:
    """
    try:
        while True:
            line = await reader.readline()
            if line == b'':
                break
            await handler.write(line)
    finally:
        await handler.close()


_DEFAULT_LIMIT = 2 ** 16  # 64 KiB


async def create_subprocess_shell(
        cmd: str,
        std_path: str,
        max_bytes: Optional[int] = 0,
        back_count: Optional[int] = 0,
        loop: Optional[AbstractEventLoop] = None,
        limit=_DEFAULT_LIMIT,
        **kwargs
) -> Process:
    """
    此接口参照 `asyncio.subprocess.create_subprocess_shell` 编写，使用自定义 SubprocessRotatingFileProtocol，
    日志将会写入到 `std_path`/pid_100.log 其中 100 是创建进程的 pid 值

    针对日志，需要说明一下， `logging.StreamHandler` 默认输出是 `sys.stderr` ，所以子进程内的日志输出都会在 `stderr_filename`
    文件中，如果需要将进程日志输出到 `stdout_filename` 则需要调整所调用程序的 `StreamHandler` ，这么做一般不太符合逻辑。
    :param cmd:
    :param std_path:
    :param max_bytes:
    :param back_count
    :param loop:
    :param limit:
    :param kwargs:  其他参数请参考 subprocess.Popen
                    https://docs.python.org/zh-cn/3.7/library/subprocess.html#subprocess.Popen
    :return:
    """
    if loop is None:
        loop = asyncio.events.get_event_loop()

    def protocol_factory():
        return SubprocessRotatingFileProtocol(
            std_path=std_path,
            max_bytes=max_bytes,
            back_count=back_count,
            limit=limit,
            loop=loop
        )

    transport, protocol = await loop.subprocess_shell(
        protocol_factory,
        cmd, stdin=None, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, **kwargs)
    return Process(transport, protocol, loop)
