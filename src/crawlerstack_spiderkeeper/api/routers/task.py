from typing import List

from fastapi import APIRouter, Depends, Response

from crawlerstack_spiderkeeper.schemas.task import Task, TaskUpdate
from crawlerstack_spiderkeeper.services import task_service
from crawlerstack_spiderkeeper.utils import CommonQueryParams

router = APIRouter()


@router.get('/tasks', response_model=List[Task])
async def get_multi(
        response: Response,
        commons: CommonQueryParams = Depends(),
):
    """
    Get tasks
    :param response:
    :param commons:
    :return:
    """
    count = await task_service.count()
    response.headers['X-Total-Count'] = str(count)
    data = []
    if count:
        data = await task_service.get_multi(
            skip=commons.skip,
            limit=commons.limit,
            order=commons.order,
            sort=commons.sort
        )
    return data


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
