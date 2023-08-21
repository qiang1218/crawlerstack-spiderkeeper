"""Base"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from crawlerstack_spiderkeeper_server.config import settings
from crawlerstack_spiderkeeper_server.data_storage.utils import Connector
from crawlerstack_spiderkeeper_server.utils import SingletonMeta
from crawlerstack_spiderkeeper_server.utils.exceptions import \
    CreateConnectionError

logger = logging.getLogger(__name__)


class Storage(metaclass=SingletonMeta):
    """Storage"""
    name: str
    _connectors: dict
    default_connector: Connector
    expire_task: asyncio.Task | None
    _server_running: bool

    expire_day = settings.EXPIRE_DAY
    expire_interval = settings.EXPIRE_INTERVAL

    def start(self, *_, **kwargs):
        """init db"""
        name = kwargs.get('name')
        url = kwargs.get('url')
        if not self._connectors.get(name):
            db, db_url = self.transform_url(url)
            conn = self.create_conn(db_url)
            if not conn:
                # 创建失败，抛出异常
                raise CreateConnectionError()
            connector = Connector(
                name=name, url=url,
                conn=conn,
                db=db,
                expire_date=datetime.now() + timedelta(self.expire_day)
            )
            self._connectors.setdefault(name, connector)
        self.default_connector = self._connectors.get(name)
        return self

    @staticmethod
    def transform_url(url: str) -> tuple:
        """transform url"""
        raise NotImplementedError

    @staticmethod
    def create_conn(config: str | dict) -> Any:
        """create db connection"""
        raise NotImplementedError

    @staticmethod
    def concat_data(fields: list, datas: list) -> list:
        """Concat data"""
        data = []
        for i in datas:
            data.append(dict(zip(fields, i)))
        return data

    @property
    def server_running(self) -> bool:
        """Server running"""
        return self._server_running

    async def server_start(self, **_):
        """Server start"""
        if self._server_running is None:
            logger.debug('Change %s.server_running to "True"', self.__class__.name)
            self._server_running = True

    async def save(self, *args, **kwargs) -> Any:
        """Save"""
        raise NotImplementedError

    async def expired(self, **_) -> Any:
        """Expired"""
        self.expire_task = asyncio.create_task(self._expiring())

    async def _expiring(self):
        while True:
            logger.debug('Server status %s', self.server_running)
            if not self.server_running:
                break
            # 遍历获取_connector中过期的对象,进行删除对象操作
            should_remove_names = []
            for key, value in self._connectors.items():
                if value.expire_date > datetime.now():
                    # 标记删除
                    should_remove_names.append(key)
            if should_remove_names:
                for name in should_remove_names:
                    self.clear(name)
            await asyncio.sleep(self.expire_interval)
        logger.debug('Stopped %s expired background task.', self.__class__.name)

    def clear(self, name) -> Any:
        """clear"""
        logger.debug("Clear connection with name: %s", name)
        try:
            self._connectors.get(name).conn.close()
        except Exception as ex:
            logger.warning('Clear connection with name: %s failed', name)
            logger.error(ex)
        self._connectors.pop(name)

    def stop(self, **kwargs) -> Any:
        """stop"""
        for _, value in self._connectors.items():
            if value.conn is not None:
                value.conn.close()

    async def server_stop(self, **_):
        """server stop"""
        logger.debug('Change %s.server_running to "False"', self.__class__.name)
        self._server_running = False
        if self.expire_task and not self.expire_task.done():
            self.expire_task.cancel('server stop!')
