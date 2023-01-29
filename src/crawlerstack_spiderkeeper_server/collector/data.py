"""storage"""
from crawlerstack_spiderkeeper_server.collector.base import BaseTask
from crawlerstack_spiderkeeper_server.services.data import DataService


class DataBackgroundTask(BaseTask):
    """Data background task"""
    NAME = 'data'

    async def callback(self, body: dict):
        """
        消费数据，并将数据写入数据目标库中。
        :param body:
        :return:
        """
        task_name = body.get('task_name')
        await DataService().create(task_name=task_name, data=body)
