"""
Executor route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_executor.messages.base import BaseMessage
from crawlerstack_spiderkeeper_executor.messages.executor import \
    ExecutorMessage
from crawlerstack_spiderkeeper_executor.schemas.base import TaskSchema
from crawlerstack_spiderkeeper_executor.services.executor import \
    ExecutorService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post('/_run', response_model=ExecutorMessage)
async def run(
        *,
        obj_in: TaskSchema,
        service: ExecutorService = Depends(),
):
    """
    Create a container
    :param obj_in:
    :param service:
    :return:
    """
    container_id = await service.run(obj_in=obj_in)
    return {'data': {'status': 'running', 'container_id': container_id}}


@router.get('/_check/{pk}', response_model=ExecutorMessage)
async def check(
        *,
        pk: str,
        service: ExecutorService = Depends(),
):
    """
    check a container
    :param pk:
    :param service:
    :return:
    """
    status = await service.check_by_id(container_id=pk)
    return {'data': {'status': status, 'container_id': pk}}


@router.get('/_rm/{pk}', response_model=BaseMessage)
async def remove(
        *,
        pk: str,
        service: ExecutorService = Depends(),
):
    """
    rm a container
    :param pk:
    :param service:
    :return:
    """
    await service.rm_by_id(container_id=pk)
    return {'message': f'Remove {pk} successfully'}
