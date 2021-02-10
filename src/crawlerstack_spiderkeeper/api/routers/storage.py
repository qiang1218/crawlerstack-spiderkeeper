from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from pydantic import BaseModel

from crawlerstack_spiderkeeper import schemas
from crawlerstack_spiderkeeper.services import storage_service
from crawlerstack_spiderkeeper.utils import AppData, AppId

router = APIRouter()


class Item(BaseModel):
    name: str


@router.post('/storage')
async def create(
        *,
        app_data: schemas.AppData
):
    await storage_service.create(AppData(**jsonable_encoder(app_data)))
    return Response(status_code=200)


@router.post('/storage/{app_id}/_start')
async def start(*, app_id: str):
    res = await storage_service.start(AppId.from_str(app_id))
    return {'res': res}


@router.post('/storage/{app_id}/_stop')
async def stop(*, app_id: str):
    res = await storage_service.stop(AppId.from_str(app_id))
    return {'res': res}
