"""
Base dao.
"""
from typing import Any, Generic, Type, Union, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from crawlerstack_spiderkeeper.utils.exceptions import (ObjectDoesNotExist, SpiderkeeperError)
from crawlerstack_spiderkeeper.utils.types import (CreateSchemaType, ModelType,
                                                   UpdateSchemaType)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base dao
    """
    model: Type[ModelType]

    def __init__(self, session=None, *args, **kwargs):
        """"""
        self._session = session

    @property
    def session(self) -> AsyncSession:
        """local session"""
        return self._session

    async def get_by_id(self, pk: Any) -> ModelType:
        """
        Get one object by id
        :param pk:
        :return:
        """
        obj = await self.session.get(self.model, pk)
        if not obj:
            raise ObjectDoesNotExist()
        return obj

    async def get(
            self,
            *,
            sorting_fields: Optional[Union[set[str], list[str]]] = None,
            search_fields: Optional[dict[str, str]] = None,
            limit: int = 5,
            offset: int = 0,
    ) -> list[ModelType]:
        """
        :return:
        """
        stmt = select(self.model)
        if sorting_fields:
            stmt = self._sort(stmt, sorting_fields)
        if search_fields:
            stmt = self._search(stmt, search_fields)
        stmt = self._paginate_by_limit_offset(stmt, limit, offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a object.
        :param obj_in:
        :return:
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        return db_obj

    def _sort(self, stmt: Select, sorting_fields: Union[tuple[str], list[str]]) -> Select:
        order_by_fields = []
        for field in sorting_fields:
            if field.startswith('-'):
                field = field[1:]
                table_field = getattr(self.model, field)
                order_by_fields.append(table_field.desc())
            else:
                table_field = getattr(self.model, field)
                order_by_fields.append(table_field.asc())
        return stmt.order_by(*order_by_fields)

    def _search(self, stmt: Select, search_fields: dict[str, str]) -> Select:
        return stmt.filter_by(**search_fields)

    def _paginate_by_limit_offset(self, stmt: Select, limit: int, offset: int) -> Select:
        """Page result by limit and offset"""
        return stmt.limit(limit).offset(offset)

    async def update(
            self,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, dict[str, Any]]
    ) -> ModelType:
        """
        Update a object.
        :param db_obj:
        :param obj_in:
        :return:
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        stmt = update(self.model).where(self.model.id == db_obj.id).values(**update_data)
        await self.session.execute(stmt)
        return db_obj

    async def update_by_id(
            self,
            *,
            pk: int,
            obj_in: Union[UpdateSchemaType, dict[str, Any]]
    ) -> ModelType:
        """
        Update by id.
        :param pk:
        :param obj_in:
        :return:
        """
        obj = await self.get_by_id(pk)
        return await self.update(db_obj=obj, obj_in=obj_in)

    async def delete(self, *, db_obj: ModelType) -> None:
        """
        Delete a object.
        :param db_obj:
        :return:
        """
        stmt = delete(self.model).where(self.model.id == db_obj.id)
        await self.session.execute(stmt)

    async def delete_by_id(self, pk: int) -> ModelType:
        """
        Delete object by id.
        :param pk:
        :return:
        """
        obj = await self.get_by_id(pk)
        return await self.delete(db_obj=obj)

    async def count(self) -> int:
        """
        Get total .
        :return:
        """
        stmt = select(func.count()).select_from(self.model)
        return await self.session.scalar(stmt)
