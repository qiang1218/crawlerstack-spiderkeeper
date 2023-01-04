"""mysql storage"""
import logging
import time
from typing import Any

import pymysql
from datetime import datetime, timedelta
from crawlerstack_spiderkeeper_server.config import settings
from crawlerstack_spiderkeeper_server.data_storage.base import Storage, Connector
from crawlerstack_spiderkeeper_server.data_storage.utils import transform_mysql_db_str

logger = logging.getLogger(__name__)


class MysqlStorage(Storage):
    name: str = 'mysql'
    _connectors = {}
    default_connector = Connector
    expire_day = settings.EXPIRE_DAY
    # TODO: open
    # expire_interval = settings.EXPIRE_INTERVAL
    expire_interval = 0.1

    def start(self, *args, **kwargs):
        """init db"""
        name = kwargs.get('name')
        url = kwargs.get('url')
        if not self._connectors.get(name):
            # 进行创建
            db_conn = self.create_db_conn(url)
            connector = Connector(
                name=name, url=url,
                conn=db_conn,
                expire_date=datetime.now() + timedelta(self.expire_day)
            )
            self._connectors.setdefault(name, connector)
        self.default_connector = self._connectors.get(name)
        return self

    def save(self, data) -> bool:
        """save"""
        # 首先进行数据组装
        sql = self.sql(tb_name=data.get('title'), fields=data.get('fields'))

        # 进行引擎判断
        conn = self.default_connector.conn
        if not conn.ping():
            # 重新链接
            logger.debug("Reconnecting with name %s", self.default_connector.name)
            pass

        # 数据存储
        cursor = conn.cursor()
        cursor.executemany(sql, data.get('datas'))
        cursor.commit()
        cursor.close()
        # 引擎过期时间更新
        self.default_connector.expire_date = datetime.now() + timedelta(self.expire_day)
        return True

    @staticmethod
    def sql(tb_name: str, fields: list):
        """sql"""
        if len(fields) == 1:
            return f"INSERT IGNORE INTO {tb_name}({fields[0]}) VALUES (%s)"

        return f"INSERT IGNORE INTO {tb_name}({','.join(fields)}) VALUES ({','.join(['%s' for _ in fields])})"

    @staticmethod
    def create_db_conn(url: str):
        """create db connection"""
        config = transform_mysql_db_str(url)
        logger.debug("Create db connection with url: %s", url)
        # pymysql连接时,port必须为int型
        config['port'] = int(config.get('port', '3306'))
        conn = pymysql.connect(**config)
        return conn

    @classmethod
    def clear(cls, name) -> Any:
        """clear"""
        logger.debug("Clear db connection with name: %s", name)
        cls._connectors.get(name).conn.close()
        cls._connectors.pop(name)

    def expired(self, **kwargs) -> Any:
        """expired"""
        while True:
            logger.info(f'Server status {self.server_running}')
            if not self.server_running:
                break
            # 遍历获取_connector中过期的对象,进行删除对象操作
            should_remove_names = []
            for key, value in self._connectors.items():
                if value.expire_date > datetime.now() or value.conn.ping():
                    # 标记删除
                    should_remove_names.append(key)
            if should_remove_names:
                for name in should_remove_names:
                    self.clear(name)
            time.sleep(self.expire_interval)

    def stop(self, **kwargs) -> Any:
        """stop"""
        for key, value in self._connectors.items():
            value.conn.close()
