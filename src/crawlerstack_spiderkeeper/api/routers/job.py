from typing import Dict, List

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper.schemas.job import Job, JobCreate, JobUpdate
from crawlerstack_spiderkeeper.services import job_service
from crawlerstack_spiderkeeper.utils import CommonQueryParams

router = APIRouter()


@router.get('/jobs/{pk}/state')
async def job_state(
        *,
        pk: int
) -> Dict[str, str]:
    result = await job_service.state(pk)
    return {
        'state': result
    }


@router.get('/jobs', response_model=List[Job])
async def get_multi(
        commons: CommonQueryParams = Depends(),
):
    """
    Get jobs
    :param commons:
    :return:
    """
    return await job_service.get_multi()


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
    res = await job_service.run(pk=pk)
    return {'res': res}


@router.post('/jobs/{pk}/_stop')
async def stop(
        *,
        pk: int,
):
    res = await job_service.stop(pk=pk)
    return {'res': res}
