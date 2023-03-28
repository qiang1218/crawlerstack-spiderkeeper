"""Data"""
from typing import Any

from crawlerstack_spiderkeeper_forwarder.forwarder.base import BaseTask


class DataPublishTask(BaseTask):
    """Data publish task"""
    NAME = 'spiderkeeper-data'

    def gen_queue_name(self, task_name: str) -> str:
        """Generate Queue name."""
        return f'{self.queue_name}-{task_name}'

    def gen_routing_key(self, task_name: str) -> str:
        """Routing key."""
        return f'{self.routing_key}-{task_name}'

    async def publish(self, body: Any, **_):
        """
        Publish message
        :param body:
        :return:
        """
        task_name = _.get('task_name')
        await self.kombu.publish(
            queue_name=self.gen_queue_name(task_name),
            routing_key=self.gen_routing_key(task_name),
            exchange_name=self.exchange_name,
            body=body
        )
