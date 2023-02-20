"""mysql storage"""
import asyncio
import json
import logging
from datetime import datetime, timedelta

import pymysql

from crawlerstack_spiderkeeper_server.data_storage.base import Storage
from crawlerstack_spiderkeeper_server.data_storage.utils import (
    Connector, transform_mysql_db_str)

logger = logging.getLogger(__name__)


class MysqlStorage(Storage):
    """mysql storage"""
    name: str = 'mysql'
    _connectors = {}
    default_connector: Connector = None
    expire_task: asyncio.Task | None = None
    _server_running = None

    @staticmethod
    def create_conn(config: dict):
        """create db connection"""
        logger.debug("Create mysql connection with url: %s", config.get('url'))
        # pymysql连接时，port必须为int型
        config['port'] = int(config.get('port', '3306'))
        try:
            conn = pymysql.connect(**config)
            return conn
        except pymysql.err.Error as ex:
            logger.error('Mysql db connection failure, url: %s', config)
            logger.error('%s', ex)
        return None

    @staticmethod
    def transform_url(url: str) -> tuple:
        """Transform url"""
        config = transform_mysql_db_str(url)
        database = config.get('database')
        return database, config

    async def save(self, data: dict) -> bool:
        """save"""
        # 首先进行数据组装
        sql = self.sql(tb_name=data.get('title'), fields=data.get('fields'))
        datas = self.format_datas(data.get('datas'))
        # 进行引擎判断
        conn = self.default_connector.conn
        conn.ping()
        # 数据存储
        with conn.cursor() as cursor:
            cursor.executemany(sql, datas)
            conn.commit()
        # 引擎过期时间更新
        self.default_connector.expire_date = datetime.now() + timedelta(self.expire_day)
        return True

    @staticmethod
    def format_datas(datas: list):
        """Format datas"""
        # 考虑爬虫数据传递过来后存在嵌套数据
        return [[json.dumps(i) if isinstance(i, (list, dict)) else i for i in data] for data in datas]

    @staticmethod
    def sql(tb_name: str, fields: list):
        """sql"""
        if len(fields) == 1:
            return f"INSERT IGNORE INTO {tb_name}({fields[0]}) VALUES (%s)"

        return f"INSERT IGNORE INTO {tb_name}({','.join(fields)}) VALUES ({','.join(['%s' for _ in fields])})"
