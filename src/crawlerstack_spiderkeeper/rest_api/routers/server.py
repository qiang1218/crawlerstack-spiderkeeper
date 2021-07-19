"""
Server route
"""
from fastapi import APIRouter, Depends, Response

from crawlerstack_spiderkeeper.schemas.server import ServerCreate, ServerUpdate
from crawlerstack_spiderkeeper.services import server_service
from crawlerstack_spiderkeeper.utils import CommonQueryParams

router = APIRouter()


@router.get('/servers')
async def get_multi(
        *,
        response: Response,
        commons: CommonQueryParams = Depends(),
):
    """
    Get multi server.
    :param response:
    :param commons:
    :return:
    """
    count = await server_service.count()
    response.headers['X-Total-Count'] = str(count)
    data = []
    if count:
        data = await server_service.get_multi(
            skip=commons.skip,
            limit=commons.limit,
            order=commons.order,
            sort=commons.sort,
        )
    return data


@router.get('/servers/{pk}')
async def get(
        *,
        pk: int,
):
    """
    Get server by id.
    :param pk:
    :return:
    """
    return await server_service.get(pk=pk)


@router.post('/servers')
async def create(
        *,
        server_in: ServerCreate,
):
    """
    Create server
    :param server_in:
    :return:
    """
    return await server_service.create(obj_in=server_in)


@router.put('/servers/{pk}')
async def put(
        *,
        pk: int,
        obj_in: ServerUpdate
):
    """
    Update a server.
    :param pk:
    :param obj_in:
    :return:
    """
    return await server_service.update(pk=pk, obj_in=obj_in)


@router.delete('/servers/{pk}')
async def delete(
        *,
        pk: int,
):
    """
    Delete a server.
    :param pk:
    :return:
    """
    return await server_service.delete(pk=pk)
