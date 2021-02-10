from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper.schemas.server import ServerCreate, ServerUpdate
from crawlerstack_spiderkeeper.services import server_service
from crawlerstack_spiderkeeper.utils import CommonQueryParams

router = APIRouter()


@router.get('/servers')
async def get_multi(
        *,
        commons: CommonQueryParams = Depends(),
):
    return await server_service.get_multi()


@router.get('/servers/{pk}')
async def get(
        *,
        pk: int,
):
    return await server_service.get(pk=pk)


@router.post('/servers')
async def create(
        *,
        server_in: ServerCreate,
):
    return await server_service.create(obj_in=server_in)


@router.put('/servers/{pk}')
async def put(
        *,
        pk: int,
        obj_in: ServerUpdate
):
    return await server_service.update(pk=pk, obj_in=obj_in)


@router.delete('/servers/{pk}')
async def delete(
        *,
        pk: int,
):
    return await server_service.delete(pk=pk)
