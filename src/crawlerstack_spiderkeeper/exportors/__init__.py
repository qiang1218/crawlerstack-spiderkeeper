"""
exporter interface
"""

# TODO Change package name. This package name spelling mistakes.

import os
from pathlib import Path
from typing import List, Optional, Type
from urllib.parse import unquote

from furl import furl


class BaseExporter:
    """
    数据导出抽象类

    """
    schema: str

    # https://github.com/gruns/furl
    # Windows:  /d:\\demo\\result.txt
    # unix: /opt/result.txt
    url: furl | None = None

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
        full_path = unquote(str(self.url.path))
        if os.name == 'nt' and full_path.startswith('/'):
            clean_path = full_path[1:]
        elif os.name != 'nt' and full_path.startswith('//'):
            clean_path = full_path[1:]
        else:
            clean_path = full_path

        file_path = Path(clean_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.client = open(file_path, 'w', encoding='utf-8')  # pylint: disable=consider-using-with

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
    Create exporter by schema.
    :param schema:
    :return:
    """
    for exporter in exports:
        if exporter.schema == schema:
            return exporter
    return None
