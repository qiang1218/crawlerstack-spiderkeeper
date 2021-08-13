"""
Storage route.
"""
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper.rest_api.utils import service_depend, auto_commit
from crawlerstack_spiderkeeper.schemas import AppData as AppDataSchema
# from crawlerstack_spiderkeeper.services import StorageService
# from crawlerstack_spiderkeeper.utils import AppData, AppId
from crawlerstack_spiderkeeper.services import StorageService
from crawlerstack_spiderkeeper.utils import AppData, AppId

router = APIRouter()


class Item(BaseModel):
    """
    Item model.
    """
    name: str


@router.post('/storage')
@auto_commit
async def create(
        *,
        app_data: AppDataSchema,
        service: service_depend(StorageService) = Depends(),
):
    """
    Save a app data to storage.
    :param app_data:
    :param service:
    :return:
    """
    await service.create(AppData(**jsonable_encoder(app_data)))
    return Response(status_code=200)


#
@router.post('/storage/{app_id}/_start')
async def start(
        *,
        app_id: str,
        service: service_depend(StorageService) = Depends(),
):
    """
    Start storage task.
    :param app_id:
    :param service:
    :return:
    """
    res = await service.start(AppId.from_str(app_id))
    return {'res': res}


@router.post('/storage/{app_id}/_stop')
async def stop(
        *,
        app_id: str,
        service: service_depend(StorageService) = Depends(),
):
    """
    Stop storage task.
    :param app_id:
    :param service:
    :return:
    """
    res = await service.stop(AppId.from_str(app_id))
    return {'res': res}
