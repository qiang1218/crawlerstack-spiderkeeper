"""mongo"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from crawlerstack_spiderkeeper_server.data_storage.base import Storage
from crawlerstack_spiderkeeper_server.data_storage.utils import (
    Connector, transform_mongo_db_str)

logger = logging.getLogger(__name__)


class MongoStorage(Storage):
    """Mongo storage"""
    name: str = 'mongo'
    _connectors = {}
    default_connector: Connector = None
    expire_task: asyncio.Task | None = None
    _server_running = None

    @staticmethod
    def create_conn(config: str):
        """create db conn"""
        # pymongo 可直接进行url连接
        logger.debug("Create mongodb connection with url: %s", config)
        try:
            conn = MongoClient(config)
            return conn
        except ConnectionFailure as ex:
            logger.error('Mongo db connection failure, url: %s', config)
            logger.error('%s', ex)
        return None

    @staticmethod
    def transform_url(url: str) -> tuple:
        """Transform url"""
        config = transform_mongo_db_str(url)
        database = config.get('database')
        db_url = config.get('url')
        return database, db_url

    @staticmethod
    def concat_data(fields: list, datas: list) -> list:
        """Concat data"""
        data = []
        for i in datas:
            data.append(dict(zip(fields, i)))
        return data

    @property
    def conn_db(self):
        """Conn db"""
        return self.default_connector.conn[self.default_connector.db]

    async def save(self, data: dict) -> bool:
        """Save"""
        # 首先进行数据组装
        tb_name = data.get('title')
        # 数据组装时
        data = self.concat_data(fields=data.get('fields'), datas=data.get('datas'))
        # 进行引擎判断
        try:
            self.conn_db[tb_name].insert_many(data)
        except ServerSelectionTimeoutError as ex:
            # 如果不存在，重新进行连接
            logger.warning('Mongo connection interrupted, try connect again, %s', ex)
            self.start(name=self.default_connector.name, url=self.default_connector.url)
            self.conn_db[tb_name].insert_many(data)

        # 引擎过期时间更新
        self.default_connector.expire_date = datetime.now() + timedelta(self.expire_day)
        return True

    def clear(self, name) -> Any:
        """clear"""
        logger.debug("Clear db connection with name: %s", name)
        self._connectors.get(name).conn.close()
        # mongo 连接关闭后，需要对引用的变量设置为 None, 让gc进行回收
        self._connectors.get(name).conn = None
        self._connectors.pop(name)

    def stop(self, **kwargs) -> Any:
        """stop"""
        for _, value in self._connectors.items():
            if value.conn is not None:
                value.conn.close()
                value.conn = None
