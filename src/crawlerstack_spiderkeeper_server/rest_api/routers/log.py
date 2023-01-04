"""log"""
import logging

from fastapi import APIRouter, Depends
from crawlerstack_spiderkeeper_server.messages.log import LogMessage
from crawlerstack_spiderkeeper_server.services.log import LogService

from crawlerstack_spiderkeeper_server.utils.extractor import log_query_extractor

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get('/logs', response_model=LogMessage)
async def get(
        *,
        query: dict = Depends(log_query_extractor),
        service: LogService = Depends(),
):
    """
    get one project by pk
    :param query:
    :param service:
    :return:
    """
    return {'data': await service.get(query)}
