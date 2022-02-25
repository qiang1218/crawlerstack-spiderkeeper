"""
Log service.
"""
import functools
import logging
from typing import Any

from kombu import Message

from crawlerstack_spiderkeeper.services.base import ICRUD
from crawlerstack_spiderkeeper.services.utils import Kombu
from crawlerstack_spiderkeeper.utils import AppId, AppData

logger = logging.getLogger(__name__)


# 注册事件


class LogService(ICRUD):
    """
    将任务运行的日志写入队列。并可以从队列读取。

    为了方便日志服务统一管理日志，使用日志服务接收任务运行的日志，
    这样日志服务就可以直接通过该服务获取所有任务的运行日志。
    """
    NAME = 'log'
    kombu = Kombu()

    def queue_name(self, app_id: AppId):
        return f'{self.NAME}-{app_id.job_id}-{app_id.task_id}'

    def routing_key(self, app_id: AppId):
        return self.queue_name(app_id)

    def consuming_and_auto_ack(self, items: list, body: Any, message: Message):  # noqa
        items.append(body)
        message.ack()

    async def get(self, app_id: AppId) -> list:
        data = []
        consume_on_response = functools.partial(self.consuming_and_auto_ack, data)
        await self.kombu.consume(
            queue_name=self.queue_name(app_id),
            routing_key=self.queue_name(app_id),
            exchange_name=self.queue_name(app_id),
            register_callbacks=[consume_on_response]
        )
        return data

    async def create(self, app_data: AppData) -> Any:
        await self.kombu.publish(
            queue_name=self.queue_name(app_data.app_id),
            routing_key=self.routing_key(app_data.app_id),
            exchange_name=self.queue_name(app_data.app_id),
            body=app_data.data
        )

    async def update(self, *args, **kwargs) -> Any:
        pass

    async def delete(self, *args, **kwargs) -> Any:
        pass
