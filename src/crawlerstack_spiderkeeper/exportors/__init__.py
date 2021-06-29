"""
exporter interface
"""

# TODO Change package name. This package name spelling mistakes.

import os
from typing import List, Optional, Type

from furl import furl


class BaseExporter:
    """
    数据导出抽象类
    """
    schema: str

    # https://github.com/gruns/furl
    url: Optional[furl] = None

    @classmethod
    def from_url(cls, url: str):
        """
        从 URL 中
        :param url:
        :return:
        """
        cls.url = furl(url)
        return cls()

    def write(self, item) -> None:
        """
        Write to destination.
        :param item:
        :return:
        """
        raise NotImplementedError

    def close(self) -> None:
        """
        Close connector.
        :return:
        """
        raise NotImplementedError


class FileExporter(BaseExporter):
    """
    url: file:///tmp/test.txt
    data will write to /tmp/test.txt
    """
    schema = 'file'

    def __init__(self):
        file_path = str(self.url.path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.client = open(file_path, 'w')  # pylint: disable=consider-using-with

    def write(self, item):
        """
        Write data to file, one item one line, and flush.
        :param item:
        :return:
        """
        self.client.write(str(item) + '\n')
        self.client.flush()

    def close(self):
        """Close it."""
        self.client.close()


exports: List[Type[BaseExporter]] = [
    FileExporter
]


def exporters_factory(schema: str) -> Optional[Type[BaseExporter]]:
    """
    Export factory.
    Create a exporter by schema.
    :param schema:
    :return:
    """
    for exporter in exports:
        if exporter.schema == schema:
            return exporter
    return None
