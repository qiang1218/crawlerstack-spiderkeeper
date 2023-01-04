"""metric"""
import logging

from fastapi import APIRouter, Depends
from crawlerstack_spiderkeeper_server.messages.metric import MetricMessage
from crawlerstack_spiderkeeper_server.services.metric import MetricService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get('/metrics', response_model=MetricMessage)
async def get(
        *,
        task_name: str,
        service: MetricService = Depends(),
):
    """
    get metric
    :param task_name:
    :param service:
    :return:
    """
    return {'data': await service.get(task_name)}
