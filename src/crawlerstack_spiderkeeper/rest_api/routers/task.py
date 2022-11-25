"""
Task route.
"""
from typing import List

from fastapi import APIRouter, Depends, Response

from crawlerstack_spiderkeeper.rest_api.utils import (auto_commit,
                                                      service_depend)
from crawlerstack_spiderkeeper.schemas.task import Task, TaskUpdate
from crawlerstack_spiderkeeper.services import TaskService, task_service
from crawlerstack_spiderkeeper.utils import CommonQueryParams

router = APIRouter()


@router.get('/tasks', response_model=List[Task])
async def get_multi(
        response: Response,
        service: service_depend(TaskService) = Depends(),
):
    """
    Get tasks
    :param response:
    :param service:
    :return:
    """
    count = await service.count()
    response.headers['X-Total-Count'] = str(count)
    data = []
    if count:
        data = await service.get()
    return data


@router.get('/tasks/{pk}', response_model=Task)
@auto_commit
async def get_by_id(
        *,
        pk: int,
        service: service_depend(TaskService) = Depends(),
):
    """
    Get one task
    :param service:
    :param pk:
    :return:
    """
    return await service.get_by_id(pk=pk)


@router.put('/tasks/{pk}', response_model=Task)
@auto_commit
async def update(
        *,
        pk: int,
        task_in: TaskUpdate,
        service: service_depend(TaskService) = Depends(),
):
    """
    Update task by id.
    :param service:
    :param pk:
    :param task_in:
    :return:
    """
    return await service.update_by_id(pk, task_in)


@router.delete('/tasks/{pk}', response_model=Task)
@auto_commit
async def delete(
        *,
        pk: int,
        service: service_depend(TaskService) = Depends(),
):
    """
    Delete one task
    :param service:
    :param pk:
    :return:
    """
    return await service.delete_by_id(pk=pk)
