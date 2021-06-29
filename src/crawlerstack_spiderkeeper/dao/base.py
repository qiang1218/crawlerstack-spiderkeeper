"""
Base dao.
"""
from typing import Any, Dict, Generic, List, Type, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import asc, desc
from sqlalchemy.orm import Query

from crawlerstack_spiderkeeper.db import ScopedSession as Session
from crawlerstack_spiderkeeper.utils import scoping_session
from crawlerstack_spiderkeeper.utils.exceptions import (ObjectDoesNotExist,
                                                        SpiderkeeperError)
from crawlerstack_spiderkeeper.utils.types import (CreateSchemaType, ModelType,
                                                   UpdateSchemaType)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base dao
    """

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    @scoping_session
    def get(self, pk: Any) -> ModelType:
        """
        Get one object by id
        :param pk:
        :return:
        """
        return self._get(pk)

    def _get(self, pk: int) -> ModelType:
        """
        Get one object by id.
        :param pk:
        :return:
        """
        obj = Session.query(self.model).get(pk)
        if not obj:
            raise ObjectDoesNotExist()
        return obj

    @scoping_session
    def get_multi(
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
        query: Query = Session.query(self.model)
        if order == 'ASC':
            query = query.order_by(asc(sort))
        elif order == 'DESC':
            query = query.order_by(desc(sort))
        query: Query = query.offset(skip).limit(limit)
        return query.all()

    def _save(self, db_obj: ModelType) -> None:  # pylint: disable=no-self-use
        Session.add(db_obj)
        Session.commit()
        Session.refresh(db_obj)

    @scoping_session
    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a object.
        :param obj_in:
        :return:
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        self._save(db_obj)
        return db_obj

    @scoping_session
    def update(
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
        return self._update(db_obj=db_obj, obj_in=obj_in)

    def _update(
            self,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update object.
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
        self._save(db_obj)
        return db_obj

    @scoping_session
    def update_by_id(
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
        obj = self._get(pk)
        return self._update(db_obj=obj, obj_in=obj_in)

    @scoping_session
    def delete(self, *, db_obj: ModelType) -> ModelType:
        """
        Delete a object.
        :param db_obj:
        :return:
        """
        return self._delete(db_obj=db_obj)

    def _delete(self, *, db_obj: ModelType) -> ModelType:  # pylint: disable=no-self-use
        """
        Delete a object.
        :param db_obj:
        :return:
        """
        Session.delete(db_obj)
        Session.commit()
        return db_obj

    @scoping_session
    def delete_by_id(self, pk: int) -> ModelType:
        """
        Delete object by id.
        :param pk:
        :return:
        """
        obj = self._get(pk)
        return self._delete(db_obj=obj)

    @scoping_session
    def count(self) -> int:
        """
        Get total .
        :return:
        """
        return Session.query(self.model).count()
