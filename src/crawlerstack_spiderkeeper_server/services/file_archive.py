"""project"""
from crawlerstack_spiderkeeper_server.models import FileArchive
from crawlerstack_spiderkeeper_server.repository.file_archive import \
    FileArchiveRepository
from crawlerstack_spiderkeeper_server.schemas.file_archive import (
    FileArchiveCreate, FileArchiveSchema, FileArchiveUpdate)
from crawlerstack_spiderkeeper_server.services.base import EntityService


class FileArchiveService(EntityService[FileArchive, FileArchiveCreate, FileArchiveUpdate, FileArchiveSchema]):
    """
    FileArchive service.
    """
    REPOSITORY_CLASS = FileArchiveRepository

    async def get_by_name(self, name) -> FileArchiveSchema:
        """
        Get a record by name
        :param name:
        :return:
        """
        # 考虑name的唯一性，故获取对应的id
        return await self.repository.get_by_name(name)
