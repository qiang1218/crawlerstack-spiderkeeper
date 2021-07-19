"""
Metric route.
"""
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from crawlerstack_spiderkeeper import schemas
from crawlerstack_spiderkeeper.services import metric_service
from crawlerstack_spiderkeeper.utils import AppData

router = APIRouter()


@router.post('/metric')
async def post(
        *,
        app_data: schemas.AppData,
):
    """
    Create metric use app data.
    :param app_data:
    :return:
    """
    await metric_service.create(AppData(**jsonable_encoder(app_data)))
    return Response(status_code=200)
