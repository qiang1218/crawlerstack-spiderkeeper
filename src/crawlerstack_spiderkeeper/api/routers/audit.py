"""
Audit route.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, Response

from crawlerstack_spiderkeeper.schemas.audit import Audit
from crawlerstack_spiderkeeper.services import audit_service
from crawlerstack_spiderkeeper.utils import CommonQueryParams

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get('/audits', response_model=List[Audit])
async def get_multi(
        *,
        response: Response,
        commons: CommonQueryParams = Depends(),
):
    """
    Get multi audits.
    :param response:
    :param commons:
    :return:
    """
    count = await audit_service.count()
    response.headers['X-Total-Count'] = str(count)
    data = []
    if count:
        data = await audit_service.get_multi(
            skip=commons.skip,
            limit=commons.limit,
            order=commons.order,
            sort=commons.sort,
        )
    return data


@router.get('/audits/{pk}')
async def get(
        *,
        pk: int,
):
    """
    Get one audit by id.
    :param pk:
    :return:
    """
    return await audit_service.get(pk=pk)

# @router.post('/audits/')
# async def create(
#         *,
#         db: Session = Depends(get_db),
#         audit_in: AuditCreate,
# ):
#     return await audit_service.create(db, audit_in=audit_in)
#
#
# @router.put('/audits/{pk}')
# async def put(
#         *,
#         pk: int,
#         db: Session = Depends(get_db),
#         project_in: AuditUpdate,
# ):
#     return await audit_service.update(db, pk=pk, project_in=project_in)
#
#
# @router.delete('/audits/{pk}')
# async def delete(
#         *,
#         pk: int,
#         db: Session = Depends(get_db),
# ):
#     return await audit_service.delete(db, pk=pk)
