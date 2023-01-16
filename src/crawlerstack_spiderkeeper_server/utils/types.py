"""
Types.
"""
from typing import TypeVar

from pydantic import \
    BaseModel as SchemaModel  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper_server.models import BaseModel

# 增加一个schema,用来将repository层返回的数据与model剥离,防止超出数据层进行数据操作
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=SchemaModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=SchemaModel)
ModelSchemaType = TypeVar('ModelSchemaType', bound=SchemaModel)
