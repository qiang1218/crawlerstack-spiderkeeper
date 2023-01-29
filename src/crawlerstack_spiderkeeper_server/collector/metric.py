"""metric"""
from crawlerstack_spiderkeeper_server.collector.base import BaseTask
from crawlerstack_spiderkeeper_server.services.metric import MetricService


class MetricBackgroundTask(BaseTask):
    """Metric background task"""
    NAME = 'metric'

    async def callback(self, body: dict):
        """
        消费数据，并将数据写入监控指标中。
        :param body:
        :return:
        """
        await MetricService().create(body)
