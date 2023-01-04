"""
Storage servers route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_server.schemas.storage_server import (StorageServerCreate,
                                                                     StorageServerUpdate)
from crawlerstack_spiderkeeper_server.services.storage_server import StorageServerService

from crawlerstack_spiderkeeper_server.messages.base import BaseMessage
from crawlerstack_spiderkeeper_server.messages.storage_server import StorageServerMessage, StorageServerMessages

from crawlerstack_spiderkeeper_server.utils.extractor import query_extractor

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/storage_servers", response_model=StorageServerMessages)
async def get_multi(
        *,
        query: dict = Depends(query_extractor),
        service: StorageServerService = Depends(),
):
    """
    Get storage_servers
    :param query:
    :param service:
    :return:
    """
    total_count = await service.count(search_fields=query.get('search_fields'))
    data = dict(**query)
    if total_count:
        items = await service.get(**query)
        data.update({'data': items, 'total_count': total_count})
    else:
        data.update({'data': []})
    return data


@router.get('/storage_servers/{pk}', response_model=StorageServerMessage)
async def get(
        *,
        pk: int,
        service: StorageServerService = Depends(),
):
    """
    get one storage_servers by pk
    :param pk:
    :param service:
    :return:
    """
    return {'data': await service.get_by_id(pk=pk)}


@router.post('/storage_servers', response_model=StorageServerMessage)
async def create(
        *,
        obj_in: StorageServerCreate,
        service: StorageServerService = Depends(),
):
    """
    create storage_server
    :param obj_in:
    :param service:
    :return:
    """
    return {'data': await service.create(obj_in=obj_in)}


@router.patch('/storage_servers/{pk}', response_model=StorageServerMessage)
async def patch(
        *,
        pk: int,
        obj_in: StorageServerUpdate,
        service: StorageServerService = Depends(),
):
    """
    Update one storage_servers's some fields
    :param pk:
    :param service:
    :param obj_in:
    :return:
    """
    return {'data': await service.update_by_id(pk=pk, obj_in=obj_in)}


@router.delete('/storage_servers/{pk}', response_model=BaseMessage)
async def delete(
        *,
        pk: int,
        service: StorageServerService = Depends(),
):
    """
    Delete one storage_servers
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)
