"""Executor"""
import logging

from fastapi import APIRouter, Depends, Request

from crawlerstack_spiderkeeper_server.messages.executor import ExecutorMessages
from crawlerstack_spiderkeeper_server.services.executor import ExecutorService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/executors", response_model=ExecutorMessages)
async def get_multi(
        *,
        request: Request,
        service: ExecutorService = Depends(),
):
    """
    Get executors
    :param request:
    :param service:
    :return:
    """
    params = dict(request.query_params)
    headers = dict(request.headers)
    return await service.get(params=params, headers=headers)
