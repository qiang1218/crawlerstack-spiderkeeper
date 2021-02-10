from typing import TypeVar

from pydantic import BaseModel as SchemaModel

from crawlerstack_spiderkeeper.db.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=SchemaModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=SchemaModel)
