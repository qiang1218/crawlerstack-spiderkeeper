"""
Job route.
"""
from typing import Dict, List

from fastapi import APIRouter, Depends, Response

from crawlerstack_spiderkeeper.schemas.job import Job, JobCreate, JobUpdate
from crawlerstack_spiderkeeper.services import job_service
from crawlerstack_spiderkeeper.utils import CommonQueryParams

router = APIRouter()


@router.get('/jobs/{pk}/state')
async def job_state(
        *,
        pk: int
) -> Dict[str, str]:
    """
    Get job state
    :param pk:
    :return:
    """
    result = await job_service.state(pk)
    return {
        'state': result
    }


@router.get('/jobs', response_model=List[Job])
async def get_multi(
        *,
        response: Response,
        commons: CommonQueryParams = Depends(),
):
    """
    Get multi job
    :param response
    :param commons:
    :return:
    :param response:
    :param commons:
    :return:
    """
    count = await job_service.count()
    response.headers['X-Total-Count'] = str(count)
    data = []
    if count:
        data = await job_service.get_multi(
            skip=commons.skip,
            limit=commons.limit,
            order=commons.order,
            sort=commons.sort
        )
    return data


@router.get('/jobs/{pk}', response_model=Job)
async def get(
        *,
        pk: int,
):
    """
    Get one job by pk
    :param pk:
    :return:
    """
    return await job_service.get(pk=pk)


@router.post('/jobs', response_model=Job)
async def create(
        *,
        job_in: JobCreate,
):
    """
    Create job
    :param job_in:
    :return:
    """
    return await job_service.create(obj_in=job_in)


@router.post('/jobs/{pk}', response_model=Job)
async def update(
        *,
        pk: int,
        job_in: JobUpdate
):
    """
    Update job by id.
    :param pk:
    :param job_in:
    :return:
    """
    return await job_service.update(pk, job_in)


@router.delete('/jobs/{pk}', response_model=Job)
async def delete(
        *,
        pk: int,
):
    """
    Delete one job
    :param pk:
    :return:
    """
    return await job_service.delete(pk=pk)


@router.post('/jobs/{pk}/_run')
async def run(
        *,
        pk: int
):
    """
    Run job by id
    :param pk:
    :return:
    """
    res = await job_service.run(pk=pk)
    return {'res': res}


@router.post('/jobs/{pk}/_stop')
async def stop(
        *,
        pk: int,
):
    """
    Stop job by id
    :param pk:
    :return:
    """
    res = await job_service.stop(pk=pk)
    return {'res': res}
