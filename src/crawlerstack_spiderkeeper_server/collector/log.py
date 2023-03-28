"""log"""
from crawlerstack_spiderkeeper_server.collector.base import BaseTask
from crawlerstack_spiderkeeper_server.services.log import LogService


class LogBackgroundTask(BaseTask):
    """Log background task"""
    NAME = 'spiderkeeper-log'

    async def callback(self, body: dict):
        """
        消费数据，并将数据写入日志文件中。
        :param body:
        :return:
        """
        await LogService().create(data=body)
