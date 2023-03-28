"""
Task route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_server.messages.base import BaseMessage
from crawlerstack_spiderkeeper_server.messages.job import JobMessage
from crawlerstack_spiderkeeper_server.messages.task import (TaskMessage,
                                                            TaskMessages)
from crawlerstack_spiderkeeper_server.schemas.task import (TaskCreate,
                                                           TaskUpdate)
from crawlerstack_spiderkeeper_server.services.task import TaskService
from crawlerstack_spiderkeeper_server.utils.extractor import query_extractor

router = APIRouter()

logger = logging.getLogger(__name__)


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
    Get one task by pk
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
    Delete one task
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)


@router.get('/tasks/{pk}/jobs', response_model=JobMessage)
async def get_job_from_task_id(
        *,
        pk: int,
        service: TaskService = Depends(),
):
    """
    get job from task_id
    :param pk:
    :param service:
    :return:
    """

    return {'data': await service.get_job_from_task_id(pk)}


@router.get('/tasks/{pk}/_start', response_model=BaseMessage)
async def start_task_consume(
        *,
        pk: int,
        service: TaskService = Depends(),
):
    """
    start task consume by id
    :param pk:
    :param service:
    :return:
    """
    return {'message': await service.start_task_consume(pk)}


@router.get('/tasks/{pk}/_stop', response_model=BaseMessage)
async def stop_task_consume(
        *,
        pk: int,
        service: TaskService = Depends(),
):
    """
    stop task consumes by id
    :param pk:
    :param service:
    :return:
    """
    return {'message': await service.stop_task_consume(pk)}


@router.get('/tasks/{pk}/_terminate', response_model=BaseMessage)
async def terminate_task_consume(
        *,
        pk: int,
        service: TaskService = Depends(),
):
    """
    stop task consumes by id
    :param pk:
    :param service:
    :return:
    """
    return {'message': await service.terminate_task_consume(pk)}
