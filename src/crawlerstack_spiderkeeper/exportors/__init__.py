import os
from typing import List, Optional, Type

from furl import furl


class BaseExporter:
    schema: str

    # https://github.com/gruns/furl
    url: Optional[furl] = None

    @classmethod
    def from_url(cls, url: str):
        cls.url = furl(url)
        return cls()

    def write(self, item) -> None:
        raise NotImplementedError

    def close(self) -> None:
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
        self.client = open(file_path, 'w')

    def write(self, item):
        self.client.write(str(item) + '\n')
        self.client.flush()

    def close(self):
        self.client.close()


exports: List[Type[BaseExporter]] = [
    FileExporter
]


def exporters_factory(schema: str) -> Optional[Type[BaseExporter]]:
    for exporter in exports:
        if exporter.schema == schema:
            return exporter
