"""
Base service.
"""

import logging
from typing import Any, Dict, Generic, Optional, Type, Union

from sqlalchemy.ext.asyncio import AsyncSession

from crawlerstack_spiderkeeper.dao import ProjectDAO
from crawlerstack_spiderkeeper.dao.base import BaseDAO
from crawlerstack_spiderkeeper.db import session_provider
from crawlerstack_spiderkeeper.db.models import Project
from crawlerstack_spiderkeeper.schemas.project import (ProjectCreate,
                                                       ProjectUpdate)
from crawlerstack_spiderkeeper.utils.types import (CreateSchemaType, ModelType,
                                                   UpdateSchemaType)

logger = logging.getLogger(__name__)


class ICRUD:  # noqa
    """
    定义接口规范。
    Service 类都需要实现该接口的抽象方法。

    根据里式替换原则：
        - 当子类的方法实现父类的方法时（重写/重载或实现抽象方法），方法的后置条件（即方法的的输出/返回值）要比父类的方法更严格或相等
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, *args, **kwargs) -> Any:
        """
        查询记录。

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def create(self, *args, **kwargs) -> Any:
        """
        创建记录。

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def update(self, *args, **kwargs) -> Any:
        """
        更新记录。

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def delete(self, *args, **kwargs) -> Any:
        """
        删除记录。

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError


class EntityService(ICRUD, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service."""
    DAO_CLASS: Type[BaseDAO]

    @property
    def dao(self):
        """DAO"""
        return self.DAO_CLASS(self.session)

    @property
    def session(self) -> AsyncSession:
        """Async session"""
        return self._session

    async def get_by_id(self, pk: int) -> ModelType:
        """Get record by primary key."""
        return await self.dao.get_by_id(pk)

    async def get(
            self,
            *,
            sorting_fields: Optional[Union[set[str], list[str]]] = None,
            search_fields: Optional[dict[str, str]] = None,
            limit: int = 5,
            offset: int = 0,
    ) -> list[ModelType]:
        """
        Get multi record.
        :param sorting_fields:
        :param search_fields:
        :param limit:
        :param offset:
        :return:
        """
        return await self.dao.get(
            sorting_fields=sorting_fields,
            search_fields=search_fields,
            limit=limit,
            offset=offset,
        )

    async def create(
            self,
            *,
            obj_in: CreateSchemaType
    ) -> ModelType:
        """
        Create a record.
        :param obj_in:
        :return:
        """
        return await self.dao.create(obj_in=obj_in)

    async def update_by_id(
            self,
            pk: int,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        :param pk:
        :param obj_in:
        :return:
        """
        return await self.dao.update_by_id(pk=pk, obj_in=obj_in)

    async def update(
            self,
            pk: int,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ):
        return await self.update_by_id(pk=pk, obj_in=obj_in)

    async def delete_by_id(self, *, pk: int) -> ModelType:
        """
        Delete a record by primary key.
        :param pk:
        :return:
        """
        return await self.dao.delete_by_id(pk)

    async def delete(self, *, pk: int) -> ModelType:
        """
        Delete a record
        :param pk:
        :return:
        """
        return await self.delete_by_id(pk=pk)

    async def count(self) -> int:
        """
        Count.
        :return:
        """
        return await self.dao.count()


class ProjectService(EntityService[Project, ProjectCreate, ProjectUpdate]):
    """
    Project service.
    """
    DAO_CLASS = ProjectDAO


class ServerEventMixin:

    @classmethod
    @session_provider(auto_commit=True)
    async def server_start_event(cls, session: AsyncSession):
        service = cls(session)  # noqa
        await service.server_start()

    async def server_start(self):
        """"""

    @classmethod
    @session_provider(auto_commit=True)
    async def server_stop_event(cls, session: AsyncSession):
        service = cls(session)  # noqa
        await service.server_stop()

    async def server_stop(self):
        """"""
