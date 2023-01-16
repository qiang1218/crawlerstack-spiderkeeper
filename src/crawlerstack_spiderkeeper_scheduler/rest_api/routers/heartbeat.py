"""
heartbeat route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_scheduler.messages.base import BaseMessage
from crawlerstack_spiderkeeper_scheduler.schemas.executor import ExecutorUpdate
from crawlerstack_spiderkeeper_scheduler.services.executor import \
    ExecutorService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post('/heartbeats/{pk}', response_model=BaseMessage)
async def heartbeat(
        *,
        pk: int,
        obj_in: ExecutorUpdate,
        service: ExecutorService = Depends(),
):
    """
    heartbeat executor
    :param obj_in:
    :param pk:
    :param service:
    :return:
    """
    return await service.heartbeat(pk=pk, obj_in=obj_in)
