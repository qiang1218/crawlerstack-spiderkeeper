"""
Job route.
"""
from typing import Dict, List

from fastapi import APIRouter, Depends, Response

from crawlerstack_spiderkeeper.rest_api.utils import (auto_commit,
                                                      service_depend)
from crawlerstack_spiderkeeper.schemas import ActionResult
from crawlerstack_spiderkeeper.schemas.job import Job, JobCreate, JobUpdate
from crawlerstack_spiderkeeper.services import JobService

router = APIRouter()


@router.get('/jobs/{pk}/status')
async def job_status(
        *,
        pk: int,
        service: service_depend(JobService) = Depends(),
) -> Dict[str, str]:
    """
    Get job status
    :param service:
    :param pk:
    :return:
    """
    result = await service.status(pk)
    return {
        'status': result
    }


@router.get('/jobs', response_model=List[Job])
async def get(
        *,
        response: Response,
        service: service_depend(JobService) = Depends(),
):
    """
    Get multi job
    :param response
    :param service:
    :return:
    """
    count = await service.count()
    response.headers['X-Total-Count'] = str(count)
    data = []
    if count:
        data = await service.get()
    return data


@router.get('/jobs/{pk}', response_model=Job)
async def get_by_id(
        *,
        pk: int,
        service: service_depend(JobService) = Depends(),
):
    """
    Get one job by pk
    :param service:
    :param pk:
    :return:
    """
    return await service.get_by_id(pk=pk)


@router.post('/jobs', response_model=Job)
@auto_commit
async def create(
        *,
        job_in: JobCreate,
        service: service_depend(JobService) = Depends(),
):
    """
    Create job
    :param service:
    :param job_in:
    :return:
    """
    return await service.create(obj_in=job_in)


@router.put('/jobs/{pk}', response_model=Job)
@auto_commit
async def update(
        *,
        pk: int,
        job_in: JobUpdate,
        service: service_depend(JobService) = Depends(),
):
    """
    Update job by id.
    :param service:
    :param pk:
    :param job_in:
    :return:
    """
    return await service.update_by_id(pk, job_in)


@router.delete('/jobs/{pk}', response_model=Job)
@auto_commit
async def delete(
        *,
        pk: int,
        service: service_depend(JobService) = Depends(),
):
    """
    Delete one job
    :param service:
    :param pk:
    :return:
    """
    return await service.delete_by_id(pk=pk)


@router.post('/jobs/{pk}/_run', response_model=ActionResult)
@auto_commit
async def run(
        *,
        pk: int,
        service: service_depend(JobService) = Depends(),
) -> ActionResult:
    """
    Run job by id
    :param service:
    :param pk:
    :return:
    """
    return await service.run(pk=pk)


@router.post('/jobs/{pk}/_stop', response_model=ActionResult)
@auto_commit
async def stop(
        *,
        pk: int,
        service: service_depend(JobService) = Depends(),
) -> ActionResult:
    """
    Stop job by id
    :param service:
    :param pk:
    :return:
    """
    return await service.stop(pk=pk)
