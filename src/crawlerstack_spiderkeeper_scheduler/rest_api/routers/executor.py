"""
Executor route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_scheduler.schemas.executor import (ExecutorCreate, ExecutorUpdate)

from crawlerstack_spiderkeeper_scheduler.services.executor import ExecutorService
from crawlerstack_spiderkeeper_scheduler.utils.extractor import query_extractor

from crawlerstack_spiderkeeper_scheduler.messages.base import BaseMessage
from crawlerstack_spiderkeeper_scheduler.messages.executor import ExecutorMessages, ExecutorMessage

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/executors", response_model=ExecutorMessages)
async def get_multi(
        *,
        query: dict = Depends(query_extractor),
        service: ExecutorService = Depends(),
):
    """
    Get executors
    :param query:
    :param service:
    :return:
    """
    total_count = await service.count(search_fields=query.get('search_fields'))
    data = dict(**query)
    if total_count:
        items = await service.get(**data)
        data.update({'data': items, 'total_count': total_count})
    else:
        data.update({'data': []})
    return data


@router.get('/executors/{pk}', response_model=ExecutorMessage)
async def get(
        *,
        pk: int,
        service: ExecutorService = Depends(),
):
    """
    get one executor by pk
    :param pk:
    :param service:
    :return:
    """
    return {'data': await service.get_by_id(pk=pk)}


@router.post('/executors', response_model=ExecutorMessage)
async def create(
        *,
        obj_in: ExecutorCreate,
        service: ExecutorService = Depends(),
):
    """
    create executor
    :param obj_in:
    :param service:
    :return:
    """
    # 考虑下游任务对创建后的数据id进行调用，故返回相关的元数据
    return {'data': await service.create(obj_in=obj_in)}


@router.patch('/executors/{pk}', response_model=ExecutorMessage)
async def patch(
        *,
        pk: int,
        obj_in: ExecutorUpdate,
        service: ExecutorService = Depends(),
):
    """
    Update one executor's some fields
    :param pk:
    :param service:
    :param obj_in:
    :return:
    """
    return {'data': await service.update_by_id(pk=pk, obj_in=obj_in)}


@router.delete('/executors/{pk}', response_model=BaseMessage)
async def delete(
        *,
        pk: int,
        service: ExecutorService = Depends(),
):
    """
    Delete one executor
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)
