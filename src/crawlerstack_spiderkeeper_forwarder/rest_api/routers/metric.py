"""
Metric route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_forwarder.messages.base import BaseMessage
from crawlerstack_spiderkeeper_forwarder.schemas.metric import MetricSchema

from crawlerstack_spiderkeeper_forwarder.services.metric import MetricService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post('/metrics', response_model=BaseMessage)
def create(
        *,
        obj_in: MetricSchema,
        service: MetricService = Depends(),
):
    """
    Create
    :param obj_in:
    :param service:
    :return:
    """
    return service.create(obj_in=obj_in)
