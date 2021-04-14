"""
Storage route.
"""
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from crawlerstack_spiderkeeper.schemas import AppData as AppDataSchema
from crawlerstack_spiderkeeper.services import storage_service
from crawlerstack_spiderkeeper.utils import AppData, AppId

# pylint: disable=too-few-public-methods

router = APIRouter()


class Item(BaseModel):
    """
    Item model.
    """
    name: str


@router.post('/storage')
async def create(
        *,
        app_data: AppDataSchema
):
    """
    Save a app data to storage.
    :param app_data:
    :return:
    """
    await storage_service.create(AppData(**jsonable_encoder(app_data)))
    return Response(status_code=200)


@router.post('/storage/{app_id}/_start')
async def start(*, app_id: str):
    """
    Start storage task.
    :param app_id:
    :return:
    """
    res = await storage_service.start(AppId.from_str(app_id))
    return {'res': res}


@router.post('/storage/{app_id}/_stop')
async def stop(*, app_id: str):
    """
    Stop storage task.
    :param app_id:
    :return:
    """
    res = await storage_service.stop(AppId.from_str(app_id))
    return {'res': res}
