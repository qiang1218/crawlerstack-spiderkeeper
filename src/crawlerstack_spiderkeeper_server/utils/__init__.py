"""Utils"""
import asyncio
import logging
import os
from asyncio import Future
from functools import partial
from pathlib import Path
from typing import Any, AsyncIterable, Callable, List, Optional, Union

import aiofiles
from aiofiles.threadpool.binary import AsyncBufferedReader

logger = logging.getLogger(__name__)

CRON_MAP = {
    '@yearly': '0 0 1 1 *',
    '@monthly': '0 0 1 * *',
    '@weekly': '0 0 * * 0',
    '@daily': '0 0 * * *',
    '@hourly': '0 * * * *'
}


class SingletonMeta(type):
    """
    单例元类

    example:
        class Foo(metaclass=SingletonMeta):...
    """
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
        return cls.__instances[cls]


def transform_cron_expression(expression: str):
    """
    Transform cron expression
    :param expression:
    :return:
    """
    if expression.startswith('@'):
        return CRON_MAP.get(expression, expression)
    return expression


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


class File:
    """
    File文件处理
    """

    def __init__(self, filename: Path):
        self.filename = filename

    async def write(self, datas: Union[List[str], tuple[str]]) -> None:
        """
        Write data to the file
        :param datas:
        :return:
        """
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        async with aiofiles.open(self.filename, 'a', encoding='utf-8') as f_obj:
            for i in datas:
                await f_obj.write(f'{i}\n')

    async def head(self, line_number: int = 50) -> AsyncIterable[str]:
        """
        获取文件前几行
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

    async def last(self, line: int = 50, buffer_size=1024) -> list[str]:
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
                await self.forward_fd(reader, buffer_size, line)
            data = []
            async for i in reader:
                data.append(i.decode())
            return data[-line:]

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

    @staticmethod
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
            await reader.seek(-offset, os.SEEK_CUR)  # 从当前位置向前调整偏移量
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
                    # 每当进行 10 次调整时，将 buffer_size
                    # 这么做可以更快速的向前调整
                    if offset_times % 10 == 0:
                        offset += buffer_size
                else:
                    if offset > buffer_size and offset_times % 10 == 0:
                        # 当统计行数大于所需要行数的一般时，
                        # 如果 offset 大于 buffer_size 则不断缩小范围
                        # 目的是获取更精确行数，而不会和预期行数偏差太大
                        offset -= buffer_size
