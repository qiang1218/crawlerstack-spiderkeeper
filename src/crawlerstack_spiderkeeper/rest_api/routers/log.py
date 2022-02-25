"""
Log api.
"""
import logging

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from crawlerstack_spiderkeeper import schemas
from crawlerstack_spiderkeeper.rest_api.utils import service_depend
from crawlerstack_spiderkeeper.services.log import LogService
from crawlerstack_spiderkeeper.utils import AppData

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/log')
async def get(
        *,
        app_id: str = None,
        service: service_depend(LogService) = Depends(),

):
    return await service.get(app_id=app_id)


@router.post('/log')
async def post(
        *,
        app_data: schemas.AppData,
        service: service_depend(LogService) = Depends(),
):
    await service.create(AppData(**jsonable_encoder(app_data)))
    return {'status': 'success'}
