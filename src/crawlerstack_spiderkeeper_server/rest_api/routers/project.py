"""
Project route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_server.messages.base import BaseMessage
from crawlerstack_spiderkeeper_server.messages.project import (ProjectMessage,
                                                               ProjectMessages)
from crawlerstack_spiderkeeper_server.schemas.project import (ProjectCreate,
                                                              ProjectUpdate)
from crawlerstack_spiderkeeper_server.services import ProjectService
from crawlerstack_spiderkeeper_server.utils.extractor import query_extractor

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/projects", response_model=ProjectMessages)
async def get_multi(
        *,
        query: dict = Depends(query_extractor),
        service: ProjectService = Depends(),
):
    """
    Get projects
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


@router.get('/projects/{pk}', response_model=ProjectMessage)
async def get(
        *,
        pk: int,
        service: ProjectService = Depends(),
):
    """
    get one project by pk
    :param pk:
    :param service:
    :return:
    """
    return {'data': await service.get_by_id(pk=pk)}


@router.post('/projects', response_model=ProjectMessage)
async def create(
        *,
        obj_in: ProjectCreate,
        service: ProjectService = Depends(),
):
    """
    create project
    :param obj_in:
    :param service:
    :return:
    """
    return {'data': await service.create(obj_in=obj_in)}


@router.patch('/projects/{pk}', response_model=ProjectMessage)
async def patch(
        *,
        pk: int,
        obj_in: ProjectUpdate,
        service: ProjectService = Depends(),
):
    """
    Update one project's some fields
    :param pk:
    :param service:
    :param obj_in:
    :return:
    """
    return {'data': await service.update_by_id(pk=pk, obj_in=obj_in)}


@router.delete('/projects/{pk}', response_model=BaseMessage)
async def delete(
        *,
        pk: int,
        service: ProjectService = Depends(),
):
    """
    Delete one project
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)
