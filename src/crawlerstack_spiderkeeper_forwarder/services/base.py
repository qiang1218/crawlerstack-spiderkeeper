"""
Base service
"""
from typing import Any, Type

from crawlerstack_spiderkeeper_forwarder.forwarder.base import BaseTask


class ICRUD:  # noqa
    """
    定义接口规范。只提供创建操作
    """

    async def create(self, *args, **kwargs) -> Any:
        """
        create
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError


class EntityService(ICRUD):
    """Entity service"""
    FORWARDER_CLASS: Type[BaseTask]

    @property
    def forwarder(self):
        """forwarder"""
        return self.FORWARDER_CLASS()

    async def create(self, obj_in: Any):
        """
        create
        :param obj_in:
        :return:
        """
        # todo 字典数据序列化

        await self.forwarder.publish(body=obj_in)
