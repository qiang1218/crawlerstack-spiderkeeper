"""file"""
import asyncio
import base64
import json
import logging
import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import boto.s3.connection
from boto.s3.key import Key
from fastapi_sa.database import session_ctx

from crawlerstack_spiderkeeper_server.config import data_path, settings
from crawlerstack_spiderkeeper_server.data_storage.base import Storage
from crawlerstack_spiderkeeper_server.data_storage.utils import (
    Connector, transform_s3_url)
from crawlerstack_spiderkeeper_server.repository.file_archive import \
    FileArchiveRepository
from crawlerstack_spiderkeeper_server.schemas.file_archive import (
    FileArchiveCreate, FileArchiveSchema)
from crawlerstack_spiderkeeper_server.utils import File
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    ObjectDoesNotExist

logger = logging.getLogger(__name__)


class StorageRecord:
    """Storage record"""
    repository = FileArchiveRepository()

    @session_ctx
    async def clear_record(self, pk) -> FileArchiveSchema:
        """Clear record"""
        return await self.repository.delete_by_id(pk=pk)

    @session_ctx
    async def get_record(self) -> list[FileArchiveSchema]:
        """Get record"""
        return await self.repository.get(search_fields={'status': '0'})

    @session_ctx
    async def get_record_by_name(self, name: str) -> FileArchiveSchema:
        """Get record by name"""
        return await self.repository.get_by_name(name)

    @session_ctx
    async def create_record(self, obj_in: FileArchiveCreate) -> FileArchiveSchema:
        """Create record"""
        return await self.repository.create(obj_in=obj_in)

    @session_ctx
    async def update_record(self, pk: int, obj_in: dict) -> FileArchiveSchema:
        """Update record"""
        return await self.repository.update_by_id(pk=pk, obj_in=obj_in)


class FileStorage(Storage):
    """s3 storage"""
    name: str = 's3'
    _connectors = {}
    default_connector: Connector = None
    expire_task: asyncio.Task | None = None
    archive_task: asyncio.Task | None = None
    _server_running = None
    file_prefix = settings.FILE_PATH_PREFIX
    _data_key_prefix = 'data/'
    _snapshot_key_prefix = 'snapshot/'
    archive_interval = settings.ARCHIVE_INTERVAL
    archive_minutes = settings.ARCHIVE_MINUTES
    repository = StorageRecord()

    @staticmethod
    def create_conn(config: dict):
        """Create s3 session"""
        host = config.get('host')
        logger.debug("Create s3 connection with url: %s", host)
        try:
            conn = boto.connect_s3(
                aws_access_key_id=config.get('access_key'),
                aws_secret_access_key=config.get('secret_key'),
                host=config.get('host'),
                is_secure=False,
                calling_format=boto.s3.connection.OrdinaryCallingFormat(),
            )
            return conn
        except Exception as ex:
            logger.error('S3 connection failure, url: %s', host)
            logger.error('%s', ex)
        return None

    @property
    def bucket(self):
        """Bucket"""
        return self.default_connector.conn.get_bucket(self.default_connector.db)

    @property
    def expired_time(self) -> int:
        """Expired timestamp in seconds"""
        return int(time.time()) + self.archive_minutes * 60

    def file_path(self, filename: str):
        """data path"""
        # 文件名合成添加连接器的name，防止多个job文件误操作
        return Path(data_path, self.file_prefix, self.default_connector.name, filename)

    @staticmethod
    def transform_url(url: str) -> tuple:
        """Transform url"""
        config = transform_s3_url(url)
        bucket = config.get('bucket')
        return bucket, config

    def new_key(self, key_name: str) -> Key:
        """New key"""
        return self.bucket.new_key(key_name)

    def upload_file(self, key_name: str, filename: str):
        """Upload file"""
        key = self.new_key(key_name)
        key.set_contents_from_filename(filename)

    def upload_string(self, key_name: str, file_str: str):
        """Upload string"""
        key = self.new_key(key_name)
        key.set_contents_from_string(file_str)

    def upload_file_name(self, key_name: str, file_name: str):
        """Upload steam"""
        key = self.new_key(key_name)
        key.set_contents_from_filename(file_name)

    def get(self, key_name: str):
        """Exists file"""
        return self.bucket.get_key(key_name)

    @staticmethod
    def gen_data_title_name(title: str) -> str:
        """Generate data  title"""
        # 周数 /%Y%W  年月日 /%Y%m%d  采用年月日的方式
        _suffix = datetime.now().strftime("/%Y%m%d")
        return title + _suffix

    @staticmethod
    def gen_snapshot_title_name(title: str, file_name: str) -> str:
        """Generate snapshot title"""
        return title + '/' + file_name

    def gen_data_key_name(self, name: str) -> str:
        """Generate data key"""
        return self._data_key_prefix + name + '.json'

    def gen_snapshot_key_name(self, name: str) -> str:
        """Generate snapshot key"""
        return self._snapshot_key_prefix + name

    @staticmethod
    def concat_data(fields: list, datas: list) -> list:
        """Concat data"""
        data = []
        for i in datas:
            data.append(json.dumps(dict(zip(fields, i))))
        return data

    async def save(self, data: dict) -> bool:
        """save"""
        snapshot_enabled = data.get('snapshot_enabled')
        if snapshot_enabled:
            # 快照保存，单文件保存，不涉及数据追加
            return await self.save_snapshot_data(data)
        return await self.save_structured_data(data)

    async def save_structured_data(self, data: dict) -> bool:
        """
        save structured data
        :param data:
        :return:
        """
        # 先对数据进行组装
        name = self.gen_data_title_name(data.get('title'))
        datas = self.concat_data(fields=data.get('fields'), datas=data.get('datas'))
        # 由于以文件对象形式保存，则需要进行文件命名操作，同一个task_name会对应多个文件，规则制定
        key_name = self.gen_data_key_name(name)
        origin_data = self.get(key_name)
        if origin_data is None:
            # 通过对key值的判断，获取存在状态
            # 第一次存储直接上传，通用格式，每条加换行，一条数据时
            self.upload_string(key_name, '\n'.join(datas) + '\n')
        else:
            # 第二次及以后
            file_local_path = self.file_path(key_name)
            # 数据库中的name需要区分多个源的情况
            storage_name = self.default_connector.name + '-' + name
            # 判断本地表的数据，如果有
            try:
                file_archives = await self.repository.get_record_by_name(storage_name)
            except ObjectDoesNotExist:
                # 先保存到本地，追加本地，创建表
                logger.debug('Initialize the local file, key: %s', name)
                # 先获取到文件
                origin_data.get_contents_to_filename(file_local_path)

                await self.repository.create_record(
                    obj_in=FileArchiveCreate(
                        name=storage_name,
                        local_path=str(file_local_path),
                        key=key_name,
                        storage_name=self.default_connector.name,
                        storage_url=self.default_connector.url,
                        expired_time=self.expired_time)
                )

            else:
                # 追加本地，更新表
                await self.repository.update_record(pk=file_archives.id, obj_in={'expired_time': self.expired_time})
            finally:
                await File(file_local_path).write(datas=datas)

        self.default_connector.expire_date = datetime.now() + timedelta(self.expire_day)
        return True

    async def save_snapshot_data(self, data: dict) -> bool:
        """
        Save snapshot data
        :param data:
        :return:
        """
        title = data.get('title')
        fields = data.get('fields')
        for i in data.get('datas'):
            try:
                row = dict(zip(fields, i))
                name = self.gen_snapshot_title_name(title, row.pop('file_name'))
                key_name = self.gen_snapshot_key_name(name)
                # 根据file_name后缀选用不同的方法
                content = row.pop('content')
                suffix = name.split('.')[-1]
                if suffix in ('xlsx', 'xls', 'pdf', 'doc', 'docs'):
                    # 生成临时文件
                    _content = base64.b64decode(content.encode('utf-8'))
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + suffix) as fp:
                        fp.write(_content)
                    self.upload_file_name(key_name, file_name=fp.name)
                    # 删除文件
                    try:
                        os.remove(fp.name)
                    except FileNotFoundError:
                        logger.warning('File not found, file name: %s', fp.name)
                else:
                    self.upload_string(key_name, content)
            except Exception as ex:
                logger.error('Save snapshot data error, exception info: %s', ex)
        return True

    async def archive(self, **_):
        """Archive"""
        # 用于后台任务对s3文件的归档操作，默认时间为2个小时操作一次，防止文件的上传延时
        self.archive_task = asyncio.create_task(self._archiving())

    async def _archiving(self):
        while True:
            logger.debug('Server status %s', self.server_running)
            if not self.server_running:
                break
            # 进行数据库中的数据获取，针对超出范围的数据，进行归档上传，记录清除
            try:
                archives = await self.repository.get_record()
                # 遍历
                for archive in archives:
                    if archive.expired_time < int(time.time()):
                        # 进行归档
                        logger.debug('Archive s3 file, key: %s', archive.key)
                        storage_name = archive.storage_name
                        connector = self._connectors.get(storage_name, None)
                        # 如果链接缺失，则进行创建
                        if not connector:
                            self.start(name=archive.storage_name, url=archive.storage_url)
                            connector = self._connectors.get(storage_name)
                        bucket = connector.conn.get_bucket(connector.db)
                        key = bucket.new_key(archive.key)
                        key.set_contents_from_filename(archive.local_path)
                        # 删除本地文件
                        await File(Path(archive.local_path)).remove()
                        # 删除本条记录，不保存流水
                        await self.repository.clear_record(archive.id)

            except ObjectDoesNotExist:
                logger.debug('No archives file')
            await asyncio.sleep(self.archive_interval)
        logger.debug('Stopped %s archived background task.', self.__class__.name)

    async def server_stop(self, **_):
        """server stop"""
        logger.debug('Change %s.server_running to "False"', self.__class__.name)
        self._server_running = False
        if self.expire_task and not self.expire_task.done():
            self.expire_task.cancel('server stop!')
        if self.archive_task and not self.archive_task.done():
            self.archive_task.cancel('server stop!')
