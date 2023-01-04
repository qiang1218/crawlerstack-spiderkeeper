"""
Log route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_forwarder.messages.base import BaseMessage
from crawlerstack_spiderkeeper_forwarder.schemas.log import LogSchema

from crawlerstack_spiderkeeper_forwarder.services.log import LogService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post('/logs', response_model=BaseMessage)
def create(
        *,
        obj_in: LogSchema,
        service: LogService = Depends(),
):
    """
    Create
    :param obj_in:
    :param service:
    :return:
    """
    return service.create(obj_in=obj_in)
