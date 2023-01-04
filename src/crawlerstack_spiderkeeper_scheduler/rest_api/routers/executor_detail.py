"""
Executor detail route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_scheduler.schemas.executor_detail import (ExecutorDetailCreate, ExecutorDetailUpdate)

from crawlerstack_spiderkeeper_scheduler.services.executor_detail import ExecutorDetailService
from crawlerstack_spiderkeeper_scheduler.utils.extractor import query_extractor

from crawlerstack_spiderkeeper_scheduler.messages.base import BaseMessage
from crawlerstack_spiderkeeper_scheduler.messages.executor_detail import ExecutorDetailMessages, ExecutorDetailMessage

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/executor_details", response_model=ExecutorDetailMessages)
async def get_multi(
        *,
        query: dict = Depends(query_extractor),
        service: ExecutorDetailService = Depends(),
):
    """
    Get executor_details
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


@router.get('/executor_details/{pk}', response_model=ExecutorDetailMessage)
async def get(
        *,
        pk: int,
        service: ExecutorDetailService = Depends(),
):
    """
    get one executor_detail by pk
    :param pk:
    :param service:
    :return:
    """
    return {'data': await service.get_by_id(pk=pk)}


@router.post('/executor_details', response_model=ExecutorDetailMessage)
async def create(
        *,
        obj_in: ExecutorDetailCreate,
        service: ExecutorDetailService = Depends(),
):
    """
    create executor_detail
    :param obj_in:
    :param service:
    :return:
    """
    # 考虑下游任务对创建后的数据id进行调用，故返回相关的元数据
    return {'data': await service.create(obj_in=obj_in)}


@router.patch('/executor_details/{pk}', response_model=ExecutorDetailMessage)
async def patch(
        *,
        pk: int,
        obj_in: ExecutorDetailUpdate,
        service: ExecutorDetailService = Depends(),
):
    """
    Update one executor_detail's some fields
    :param pk:
    :param service:
    :param obj_in:
    :return:
    """
    return {'data': await service.update_by_id(pk=pk, obj_in=obj_in)}


@router.delete('/executor_details/{pk}', response_model=BaseMessage)
async def delete(
        *,
        pk: int,
        service: ExecutorDetailService = Depends(),
):
    """
    Delete one executor_detail
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)
