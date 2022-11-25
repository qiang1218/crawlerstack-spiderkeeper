"""
Server route
"""
from fastapi import APIRouter, Depends, Response

from crawlerstack_spiderkeeper.rest_api.utils import (auto_commit,
                                                      service_depend)
from crawlerstack_spiderkeeper.schemas.server import (Server, ServerCreate,
                                                      ServerUpdate)
from crawlerstack_spiderkeeper.services import ServerService

router = APIRouter()


@router.get('/servers', response_model=list[Server])
async def get(
        *,
        response: Response,
        service: service_depend(ServerService) = Depends(),
):
    """
    Get multi server.
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


@router.get('/servers/{pk}', response_model=Server)
async def get_by_id(
        *,
        pk: int,
        service: service_depend(ServerService) = Depends(),
):
    """
    Get server by id.
    :param pk:
    :param service:
    :return:
    """
    return await service.get_by_id(pk=pk)


@router.post('/servers', response_model=Server)
@auto_commit
async def create(
        *,
        server_in: ServerCreate,
        service: service_depend(ServerService) = Depends(),
):
    """
    Create server
    :param server_in:
    :param service:
    :return:
    """
    return await service.create(obj_in=server_in)


@router.put('/servers/{pk}', response_model=Server)
@auto_commit
async def put(
        *,
        pk: int,
        obj_in: ServerUpdate,
        service: service_depend(ServerService) = Depends(),
):
    """
    Update a server.
    :param pk:
    :param obj_in:
    :param service:
    :return:
    """
    return await service.update_by_id(pk=pk, obj_in=obj_in)


@router.delete('/servers/{pk}')
@auto_commit
async def delete(
        *,
        pk: int,
        service: service_depend(ServerService) = Depends(),
):
    """
    Delete a server.
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)
