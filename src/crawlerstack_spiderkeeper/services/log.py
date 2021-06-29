"""
Log service.
"""
import functools
from typing import Any, Dict, List

from kombu import Message

from crawlerstack_spiderkeeper.services.base import KombuMixin


class LogService(KombuMixin):
    """
    日志服务接受爬虫程序自身产生的日志，将日志写入队列。同时对外提供搞获取日志的接口
    """
    exchange_name = 'log'

    async def get(self, app_id=None, limit=1):
        """
        Get log.
        :param app_id:
        :param limit:
        :return:
        """
        _buffered_data = []
        consume_on_response = functools.partial(self.consume_on_response, _buffered_data)
        await self.consume(
            self.queue_name(app_id),
            self.routing_key(app_id),
            [consume_on_response],
            limit
        )
        return _buffered_data

    def consume_on_response(self, buffered_data: List[Any], body: Dict, message: Message):
        """
        字方法用于注册到缴费者的回调。buffered_data 为接收外部存储字段，后面两个参数
        是回调的时候传入消息内容。
        在注册回调钱，请使用高阶函数 `functools.partial` 将提前定义好的变量封装到
        该方法中。带方法执行完成，提前定义的 buffered_data 就有数据了。
        :param buffered_data:
        :param body:
        :param message:
        :return:
        """
        buffered_data.append(body)
        self.logger.debug('Consuming data: %s', body)
        message.ack()

# log = LogService()
