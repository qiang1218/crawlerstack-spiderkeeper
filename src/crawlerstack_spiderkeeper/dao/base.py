"""
Base dao.
"""
from typing import Any, Dict, Generic, List, Type, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import asc, desc, select, update, delete, func

from crawlerstack_spiderkeeper.db import ScopedSession
from crawlerstack_spiderkeeper.utils.exceptions import (ObjectDoesNotExist,
                                                        SpiderkeeperError)
from crawlerstack_spiderkeeper.utils.types import (CreateSchemaType, ModelType,
                                                   UpdateSchemaType)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base dao
    """
    model: Type[ModelType]

    def __init__(self, session=None, *args, **kwargs):
        """"""

    async def get(self, pk: Any) -> ModelType:
        """
        Get one object by id
        :param pk:
        :return:
        """
        obj = await ScopedSession.get(self.model, pk)
        if not obj:
            raise ObjectDoesNotExist()
        return obj

    async def get_multi(
            self,
            *,
            skip: int = 0,
            limit: int = 100,
            order: str = 'DESC',
            sort: str = 'id',
    ) -> List[ModelType]:
        """
        Get multi objets.
        :param skip:
        :param limit:
        :param order: ASC | DESC
        :param sort:
        :return:
        :raise If sort field not in table, raise exception
        """
        if sort not in self.model.__table__.columns:
            raise SpiderkeeperError(
                f'Sort field <{sort}> not in table <{self.model.__tablename__}>'
            )
        stmt = select(self.model)
        if order == 'ASC':
            stmt = stmt.order_by(asc(sort))
        elif order == 'DESC':
            stmt = stmt.order_by(desc(sort))
        stmt = stmt.offset(skip).limit(limit)
        result = await ScopedSession.execute(stmt)
        return result.scalars().all()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a object.
        :param obj_in:
        :return:
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        ScopedSession.add(db_obj)
        return db_obj

    async def update(
            self,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
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
        await ScopedSession.execute(stmt)
        return db_obj

    async def update_by_id(
            self,
            *,
            pk: int,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update by id.
        :param pk:
        :param obj_in:
        :return:
        """
        obj = await self.get(pk)
        return self.update(db_obj=obj, obj_in=obj_in)

    async def delete(self, *, db_obj: ModelType) -> None:
        """
        Delete a object.
        :param db_obj:
        :return:
        """
        stmt = delete(self.model).where(self.model.id == db_obj.id)
        await ScopedSession.execute(stmt)

    async def delete_by_id(self, pk: int) -> ModelType:
        """
        Delete object by id.
        :param pk:
        :return:
        """
        obj = await self.get(pk)
        return await self.delete(db_obj=obj)

    async def count(self) -> int:
        """
        Get total .
        :return:
        """
        stmt = select(func.count()).select_from(self.model)
        return await ScopedSession.scalar(stmt)
