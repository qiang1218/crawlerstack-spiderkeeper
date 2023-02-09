"""base"""
import logging
from typing import Any

from crawlerstack_spiderkeeper_forwarder.forwarder.utils import Kombu

# 提供消息队列的基本操作，用来进行日志，指标，数据的收集，由各子服务实现对应功能
logger = logging.getLogger(__name__)


class BaseTask:
    """Base task"""
    NAME = 'BASE'
    kombu = Kombu()

    @property
    def queue_name(self):
        """Queue name."""
        return self.NAME

    @property
    def routing_key(self):
        """Routing key."""
        return self.NAME

    @property
    def exchange_name(self):
        """Exchange name."""
        return self.NAME

    async def publish(self, body: Any):
        """
        Publish message
        :param body:
        :return:
        """
        await self.kombu.publish(
            queue_name=self.queue_name,
            routing_key=self.routing_key,
            exchange_name=self.exchange_name,
            body=body
        )
