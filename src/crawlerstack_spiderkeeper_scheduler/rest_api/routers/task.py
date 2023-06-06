"""
Task route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_scheduler.messages.base import BaseMessage
from crawlerstack_spiderkeeper_scheduler.messages.task import (
    TaskCountMessage, TaskMessage, TaskMessages)
from crawlerstack_spiderkeeper_scheduler.schemas.task import (TaskCreate,
                                                              TaskUpdate)
from crawlerstack_spiderkeeper_scheduler.services.task import TaskService
from crawlerstack_spiderkeeper_scheduler.utils.extractor import (
    query_count_extractor, query_extractor)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/tasks/count", response_model=TaskCountMessage)
async def get_task_count(
        *,
        query: dict = Depends(query_count_extractor),
        service: TaskService = Depends(),
):
    """
    Get tasks
    :param query:
    :param service:
    :return:
    """
    total_count = await service.count(search_fields=query.get('search_fields'))
    return {'data': {'count': total_count}}


@router.get("/tasks", response_model=TaskMessages)
async def get_multi(
        *,
        query: dict = Depends(query_extractor),
        service: TaskService = Depends(),
):
    """
    Get tasks
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


@router.get('/tasks/{pk}', response_model=TaskMessage)
async def get(
        *,
        pk: int,
        service: TaskService = Depends(),
):
    """
    get one task by pk
    :param pk:
    :param service:
    :return:
    """
    return {'data': await service.get_by_id(pk=pk)}


@router.post('/tasks', response_model=TaskMessage)
async def create(
        *,
        obj_in: TaskCreate,
        service: TaskService = Depends(),
):
    """
    create task
    :param obj_in:
    :param service:
    :return:
    """
    return {'data': await service.create(obj_in=obj_in)}


@router.patch('/tasks/{pk}', response_model=TaskMessage)
async def patch(
        *,
        pk: int,
        obj_in: TaskUpdate,
        service: TaskService = Depends(),
):
    """
    Update one task's some fields
    :param pk:
    :param service:
    :param obj_in:
    :return:
    """
    return {'data': await service.update_by_id(pk=pk, obj_in=obj_in)}


@router.delete('/tasks/{pk}', response_model=BaseMessage)
async def delete(
        *,
        pk: int,
        service: TaskService = Depends(),
):
    """
    Delete one executor_detail
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)
