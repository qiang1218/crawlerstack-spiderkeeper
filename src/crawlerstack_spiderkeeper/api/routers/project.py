"""
Project route
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, Response

from crawlerstack_spiderkeeper.api.route_class import AuditRoute
from crawlerstack_spiderkeeper.schemas.project import (Project, ProjectCreate,
                                                       ProjectUpdate)
from crawlerstack_spiderkeeper.services import project_service
from crawlerstack_spiderkeeper.utils import CommonQueryParams

router = APIRouter(route_class=AuditRoute)

logger = logging.getLogger(__name__)


@router.get("/projects", response_model=List[Project])
async def get_multi(
        *,
        response: Response,
        commons: CommonQueryParams = Depends(),
):
    """
    Get projects
    :param response:
    :param commons:
    :return:
    """
    total_count = await project_service.count()
    # Set total count to header
    response.headers['X-Total-Count'] = str(total_count)
    data = []
    # If no data, we did not execute select op.
    if total_count:
        data = await project_service.get_multi(
            skip=commons.skip,
            limit=commons.limit,
            order=commons.order,
            sort=commons.sort
        )
    return data


@router.get('/projects/{pk}', response_model=Project)
async def get(
        *,
        pk: int,
):
    """
    get one project by pk
    :param pk:
    :return:
    """
    return await project_service.get(pk=pk)


@router.post('/projects', response_model=Project)
async def create(
        *,
        project_in: ProjectCreate,
):
    """
    create project
    :param project_in:
    :return:
    """
    return await project_service.create(obj_in=project_in)


@router.put('/projects/{pk}', response_model=Project)
async def put(
        *,
        pk: int,
        project_in: ProjectUpdate,
):
    """
    Update one project's some fields
    :param pk:
    :param db:
    :param project_in:
    :return:
    """
    return await project_service.update(pk=pk, obj_in=project_in)


@router.delete('/projects/{pk}', response_model=Project)
async def delete(
        *,
        pk: int,
):
    """
    Delete one project
    :param pk:
    :param db:
    :return:
    """
    return await project_service.delete(pk=pk)
