"""storage"""
from typing import Dict

from kombu import Message

from crawlerstack_spiderkeeper_server.collectior.base import BaseTask
from crawlerstack_spiderkeeper_server.services.data import DataService


class DataBackgroundTask(BaseTask):
    """Data background task"""
    NAME = 'data'

    async def consume_on_response(self, body: Dict, message: Message):
        """
        消费数据，并将数据写入数据目标库中。
        :param body:
        :param message:
        :return:
        """
        task_name = body.get('task_name')
        await DataService().create(task_name=task_name, data=body)
        message.ack()
