"""
Project route
"""
import logging

from fastapi import APIRouter, Depends, Response

from crawlerstack_spiderkeeper.rest_api.route_class import AuditRoute
from crawlerstack_spiderkeeper.rest_api.utils import (auto_commit,
                                                      service_depend)
from crawlerstack_spiderkeeper.schemas.project import (Project, ProjectCreate,
                                                       ProjectUpdate)
from crawlerstack_spiderkeeper.services import ProjectService

router = APIRouter(
    route_class=AuditRoute
)

logger = logging.getLogger(__name__)


@router.get("/projects", response_model=list[Project])
async def get_multi(
        *,
        response: Response,
        service: service_depend(ProjectService) = Depends(),
):
    """
    Get projects
    :param response:
    :param service:
    :return:
    """
    total_count = await service.count()
    # Set total count to header
    response.headers['X-Total-Count'] = str(total_count)
    data = []
    # If no data, we did not execute select op.
    if total_count:
        data = await service.get()
    return data


@router.get('/projects/{pk}', response_model=Project)
async def get(
        *,
        pk: int,
        service: service_depend(ProjectService) = Depends(),
):
    """
    get one project by pk
    :param pk:
    :param service:
    :return:
    """
    return await service.get_by_id(pk=pk)


@router.post('/projects', response_model=Project)
@auto_commit
async def create(
        *,
        project_in: ProjectCreate,
        service: service_depend(ProjectService) = Depends(),
):
    """
    create project
    :param project_in:
    :param service:
    :return:
    """
    return await service.create(obj_in=project_in)


@router.put('/projects/{pk}', response_model=Project)
@auto_commit
async def put(
        *,
        pk: int,
        project_in: ProjectUpdate,
        service: service_depend(ProjectService) = Depends(),
):
    """
    Update one project's some fields
    :param pk:
    :param service:
    :param project_in:
    :return:
    """
    return await service.update_by_id(pk=pk, obj_in=project_in)


@router.delete('/projects/{pk}', response_model=Project)
@auto_commit
async def delete(
        *,
        pk: int,
        service: service_depend(ProjectService) = Depends(),
):
    """
    Delete one project
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)
