"""Data"""
from crawlerstack_spiderkeeper_forwarder.forwarder.data import DataPublishTask
from crawlerstack_spiderkeeper_forwarder.schemas.data import DataSchema
from crawlerstack_spiderkeeper_forwarder.services.base import EntityService


class DataService(EntityService):
    """Data service"""
    FORWARDER_CLASS = DataPublishTask

    async def create(self, obj_in: DataSchema, **_) -> dict:
        """
        Create
        :param obj_in:
        :return:
        """
        body = obj_in.json()
        task_name = obj_in.task_name
        await self.forwarder.publish(body=body, task_name=task_name)
        return {}
