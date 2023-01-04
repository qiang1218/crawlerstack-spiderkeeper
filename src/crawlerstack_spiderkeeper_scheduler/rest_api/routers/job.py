"""
Job route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_scheduler.services.job import JobService
from crawlerstack_spiderkeeper_scheduler.messages.base import BaseMessage


router = APIRouter()

logger = logging.getLogger(__name__)


@router.get('/jobs/{pk}/_start', response_model=BaseMessage)
def start(
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
    return service.start_by_id(job_id=pk)


@router.get('/jobs/{pk}/_stop', response_model=BaseMessage)
def stop(
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
    return service.stop_by_id(job_id=pk)


@router.get('/jobs/{pk}/_pause', response_model=BaseMessage)
def pause(
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
    return service.pause_by_id(job_id=pk)


@router.get('/jobs/{pk}/_unpause', response_model=BaseMessage)
def unpause(
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
    return service.unpause_by_id(job_id=pk)
