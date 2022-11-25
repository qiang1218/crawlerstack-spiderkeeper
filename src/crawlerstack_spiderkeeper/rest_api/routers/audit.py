"""
Audit route.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, Response

from crawlerstack_spiderkeeper.rest_api.utils import service_depend
from crawlerstack_spiderkeeper.schemas.audit import Audit
from crawlerstack_spiderkeeper.services import AuditService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get('/audits', response_model=List[Audit])
async def get_multi(
        *,
        response: Response,
        service: service_depend(AuditService) = Depends(),
):
    """
    Get multi audits.
    :param response:
    :param commons:
    :param service:
    :return:
    """
    count = await service.count()
    response.headers['X-Total-Count'] = str(count)
    data = []
    if count:
        data = await service.get()
    return data


@router.get('/audits/{pk}')
async def get(
        *,
        pk: int,
        service: service_depend(AuditService) = Depends(),
):
    """
    Get one audit by id.
    :param service:
    :param pk:
    :return:
    """
    return await service.get_by_id(pk=pk)
