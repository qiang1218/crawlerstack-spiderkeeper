"""
Log service.
"""
import functools
import logging
from typing import Any

from kombu import Message

from crawlerstack_spiderkeeper.services.base import ICRUD
from crawlerstack_spiderkeeper.services.utils import Kombu
from crawlerstack_spiderkeeper.utils import AppData, AppId

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
        """
        queue name.

        :param app_id:
        :return:
        """
        return f'{self.NAME}-{app_id.job_id}-{app_id.task_id}'

    def routing_key(self, app_id: AppId):
        """
        routing key.

        :param app_id:
        :return:
        """
        return self.queue_name(app_id)

    def consuming_and_auto_ack(self, items: list, body: Any, message: Message):  # noqa
        """
        消费并自动 ACK 。
        :param items:
        :param body:
        :param message:
        :return:
        """
        items.append(body)
        message.ack()

    async def get(self, app_id: AppId) -> list:
        """
        获取一条日志。

        :param app_id:
        :return:
        """
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
        """
        创建一条日志。

        :param app_data:
        :return:
        """
        await self.kombu.publish(
            queue_name=self.queue_name(app_data.app_id),
            routing_key=self.routing_key(app_data.app_id),
            exchange_name=self.queue_name(app_data.app_id),
            body=app_data.data
        )

    async def update(self, *args, **kwargs) -> Any:
        """更新一条记录。"""
        pass

    async def delete(self, *args, **kwargs) -> Any:
        """删除一条日志。"""
        pass
