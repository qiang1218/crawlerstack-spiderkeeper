from typing import List

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper.schemas.task import Task, TaskUpdate
from crawlerstack_spiderkeeper.services import task_service
from crawlerstack_spiderkeeper.utils import CommonQueryParams

router = APIRouter()


@router.get('/tasks', response_model=List[Task])
async def get_multi(
        common: CommonQueryParams = Depends(),
):
    """
    Get tasks
    :param common:
    :return:
    """
    return await task_service.get_multi()


@router.get('/tasks/{pk}', response_model=Task)
async def get(
        *,
        pk: int,
):
    """
    Get one task
    :param pk:
    :return:
    """
    return await task_service.get(pk=pk)


@router.put('/tasks/{pk}', response_model=Task)
async def update(
        *,
        pk: int,
        task_in: TaskUpdate,
):
    return await task_service.update(pk, task_in)


@router.delete('/tasks/{pk}', response_model=Task)
async def delete(
        *,
        pk: int,
):
    """
    Delete one task
    :param pk:
    :return:
    """
    return await task_service.delete(pk=pk)
