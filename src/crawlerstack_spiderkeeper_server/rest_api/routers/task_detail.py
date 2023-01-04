"""
Task detail route
"""
import logging

from fastapi import APIRouter, Depends
from crawlerstack_spiderkeeper_server.messages.job import JobMessage
from crawlerstack_spiderkeeper_server.schemas.task_detail import TaskDetailCreate, TaskDetailUpdate
from crawlerstack_spiderkeeper_server.services.task_detail import TaskDetailService

from crawlerstack_spiderkeeper_server.messages.base import BaseMessage
from crawlerstack_spiderkeeper_server.messages.task_detail import TaskDetailMessage, TaskDetailMessages

from crawlerstack_spiderkeeper_server.utils.extractor import query_extractor

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/task_details", response_model=TaskDetailMessages)
async def get_multi(
        *,
        query: dict = Depends(query_extractor),
        service: TaskDetailService = Depends(),
):
    """
    Get task details
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


@router.get('/task_details/{pk}', response_model=TaskDetailMessage)
async def get(
        *,
        pk: int,
        service: TaskDetailService = Depends(),
):
    """
    get one task detail by pk
    :param pk:
    :param service:
    :return:
    """
    return {'data': await service.get_by_id(pk=pk)}


@router.post('/task_details', response_model=TaskDetailMessage)
async def create(
        *,
        obj_in: TaskDetailCreate,
        service: TaskDetailService = Depends(),
):
    """
    create task detail
    :param obj_in:
    :param service:
    :return:
    """
    return {'data': await service.create(obj_in=obj_in)}


@router.patch('/task_details/{pk}', response_model=TaskDetailMessage)
async def patch(
        *,
        pk: int,
        obj_in: TaskDetailUpdate,
        service: TaskDetailService = Depends(),
):
    """
    Update one task_detail's some fields
    :param pk:
    :param service:
    :param obj_in:
    :return:
    """
    return {'data': await service.update_by_id(pk=pk, obj_in=obj_in)}


@router.delete('/task_details/{pk}', response_model=BaseMessage)
async def delete(
        *,
        pk: int,
        service: TaskDetailService = Depends(),
):
    """
    Delete one task detail
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)


@router.get('/task_details/{pk}/tasks', response_model=JobMessage)
async def get_task_from_task_detail_id(
        *,
        pk: int,
        service: TaskDetailService = Depends(),
):
    """
    get task from task detail id
    :param pk:
    :param service:
    :return:
    """

    return {'data': await service.get_task_from_task_detail_id(pk)}
