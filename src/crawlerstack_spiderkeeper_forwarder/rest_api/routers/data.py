"""
Data route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_forwarder.messages.base import BaseMessage
from crawlerstack_spiderkeeper_forwarder.schemas.data import DataSchema
from crawlerstack_spiderkeeper_forwarder.services.data import DataService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post('/datas', response_model=BaseMessage)
def create(
        *,
        obj_in: DataSchema,
        service: DataService = Depends(),
):
    """
    Create
    :param obj_in:
    :param service:
    :return:
    """
    return service.create(obj_in=obj_in)
