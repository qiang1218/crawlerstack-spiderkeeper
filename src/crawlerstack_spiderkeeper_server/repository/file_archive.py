"""FileArchive"""
from sqlalchemy import select

from crawlerstack_spiderkeeper_server.models import FileArchive
from crawlerstack_spiderkeeper_server.repository.base import BaseRepository
from crawlerstack_spiderkeeper_server.schemas.file_archive import (
    FileArchiveCreate, FileArchiveSchema, FileArchiveUpdate)
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist


class FileArchiveRepository(BaseRepository[FileArchive, FileArchiveCreate, FileArchiveUpdate, FileArchiveSchema]):
    """
    File archive repository
    """
    model = FileArchive
    model_schema = FileArchiveSchema

    async def get_by_name(self, name: str) -> FileArchiveSchema:
        """
        get task detail from task name
        :param name:
        :return:
        """
        # 从上向下取会有多指情况，结合task 和 task_detail 关系为 1对1
        stmt = select(FileArchive).filter(FileArchive.name == name)
        file_archives: FileArchive = await self.session.scalar(stmt)
        if not file_archives:
            # Task does not exist
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(file_archives)
