"""log"""
from typing import Dict

from kombu import Message

from crawlerstack_spiderkeeper_server.collector.base import BaseTask
from crawlerstack_spiderkeeper_server.services.log import LogService


class LogBackgroundTask(BaseTask):
    """Log background task"""
    NAME = 'log'

    async def consume_on_response(self, body: Dict, message: Message):
        """
        消费数据，并将数据写入日志文件中。
        :param body:
        :param message:
        :return:
        """
        await LogService().create(data=body)
        message.ack()
