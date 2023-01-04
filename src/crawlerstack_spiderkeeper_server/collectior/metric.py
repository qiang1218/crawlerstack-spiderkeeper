"""metric collector"""
import logging
from typing import Dict

from kombu import Message
from crawlerstack_spiderkeeper_server.collectior.base import BaseTask
from crawlerstack_spiderkeeper_server.services.metric import MetricService

logger = logging.getLogger(__name__)


class MetricBackgroundTask(BaseTask):
    """Metric background task"""
    NAME = 'metric'

    async def consume_on_response(self, body: Dict, message: Message):
        """
        消费数据，并将数据写入监控指标中。
        :param body:
        :param message:
        :return:
        """
        await MetricService().create(body)
        message.ack()

