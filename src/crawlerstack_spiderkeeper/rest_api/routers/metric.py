"""
Metric route.
"""
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from crawlerstack_spiderkeeper import schemas
from crawlerstack_spiderkeeper.rest_api.utils import service_depend
from crawlerstack_spiderkeeper.services import MetricService, metric_service
from crawlerstack_spiderkeeper.utils import AppData

router = APIRouter()


@router.post('/metric')
async def post(
        *,
        app_data: schemas.AppData,
        service: service_depend(MetricService) = Depends(),
):
    """
    Create metric use app data.
    :param service:
    :param app_data:
    :return:
    """
    await service.create_msg(AppData(**jsonable_encoder(app_data)))
    return Response(status_code=200)
