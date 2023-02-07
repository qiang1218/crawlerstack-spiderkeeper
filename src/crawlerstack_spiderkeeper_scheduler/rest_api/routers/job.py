"""
Job route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_scheduler.messages.base import BaseMessage
from crawlerstack_spiderkeeper_scheduler.services.job import JobService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get('/jobs/{pk}/_start', response_model=BaseMessage)
async def start(
        *,
        pk: str,
        service: JobService = Depends(),
):
    """
    Run one project
    :param pk:
    :param service:
    :return:
    """
    return await service.start_by_id(job_id=pk)


@router.get('/jobs/{pk}/_stop', response_model=BaseMessage)
async def stop(
        *,
        pk: str,
        service: JobService = Depends(),
):
    """
    Stop one project
    :param pk:
    :param service:
    :return:
    """
    return await service.stop_by_id(job_id=pk)


@router.get('/jobs/{pk}/_pause', response_model=BaseMessage)
async def pause(
        *,
        pk: str,
        service: JobService = Depends(),
):
    """
    Pause one project
    :param pk:
    :param service:
    :return:
    """
    return await service.pause_by_id(job_id=pk)


@router.get('/jobs/{pk}/_unpause', response_model=BaseMessage)
async def unpause(
        *,
        pk: str,
        service: JobService = Depends(),
):
    """
    Unpause one project
    :param pk:
    :param service:
    :return:
    """
    return await service.unpause_by_id(job_id=pk)
