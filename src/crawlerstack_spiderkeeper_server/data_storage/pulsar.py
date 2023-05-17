"""pulsar"""
import asyncio
import json
import logging
from datetime import datetime, timedelta

from pulsar import AuthenticationToken, Client, exceptions, schema

from crawlerstack_spiderkeeper_server.data_storage import Storage
from crawlerstack_spiderkeeper_server.data_storage.utils import (
    Connector, transform_pulsar_url)

logger = logging.getLogger(__name__)


class PulsarStorage(Storage):
    """PulsarStorage"""
    name: str = 'pulsar'
    _connectors = {}
    default_connector: Connector = None
    expire_task: asyncio.Task | None = None
    _server_running = None

    @staticmethod
    def create_conn(config: dict):
        """Create pulsar connection"""
        url = config.get('url')
        token = config.get('token')
        logger.debug("Create mysql connection with url: %s", config)
        try:
            conn = Client(service_url=url, authentication=AuthenticationToken(token), connection_timeout_ms=3000,
                          operation_timeout_seconds=1)
            producer = conn.create_producer('test')
            producer.close()
            return conn
        except exceptions.PulsarException as ex:
            logger.error("Failed to create pulsar connection, exception info: %s", ex)
        return None

    @staticmethod
    def transform_url(url: str) -> tuple:
        """Transform url"""
        config = transform_pulsar_url(url)
        topic_prefix = config.get('topic_prefix')
        return topic_prefix, config

    def publish_data(self, topic_name: str, data: list):
        """
        Publish data
        :param topic_name:
        :param data:
        :return:
        """
        # 考虑数据单条上传后续处理较方便
        # 1. 声明主题
        producer = self.default_connector.conn.create_producer(
            topic_name,
            schema=schema.StringSchema())
        for i in data:
            producer.send(content=json.dumps(i))

        if producer.is_connected():
            producer.close()

    async def save(self, data: dict) -> bool:
        """Save"""
        # 数据的保存
        # 1. topic的创建
        topic_name = 'persistent://' + self.default_connector.db + '/' + data.get('title')
        data = self.concat_data(fields=data.get('fields'), datas=data.get('datas'))

        # 2. 数据转发到topic, 转发前数据格式的转换
        try:
            self.publish_data(topic_name, data)
        except exceptions.PulsarException as ex:
            logger.error('Failed Send data to topic: %s, exception info: %s', topic_name, ex)
            self.start(name=self.default_connector.name, url=self.default_connector.url)
            self.publish_data(topic_name, data)

        self.default_connector.expire_date = datetime.now() + timedelta(self.expire_day)
        return True
