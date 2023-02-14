"""
Job route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_server.messages.artifact import ArtifactMessage
from crawlerstack_spiderkeeper_server.messages.base import BaseMessage
from crawlerstack_spiderkeeper_server.messages.job import (JobMessage,
                                                           JobMessages)
from crawlerstack_spiderkeeper_server.messages.storage_server import \
    StorageServerMessage
from crawlerstack_spiderkeeper_server.schemas.job import JobCreate, JobUpdate
from crawlerstack_spiderkeeper_server.services.job import JobService
from crawlerstack_spiderkeeper_server.utils.extractor import query_extractor

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/jobs", response_model=JobMessages)
async def get_multi(
        *,
        query: dict = Depends(query_extractor),
        service: JobService = Depends(),
):
    """
    Get jobs
    :param query:
    :param service:
    :return:
    """
    total_count = await service.count(search_fields=query.get('search_fields'))
    data = dict(**query)
    if total_count:
        items = await service.get(**data)
        data.update({'data': items, 'total_count': total_count})
    else:
        data.update({'data': []})
    return data


@router.get('/jobs/{pk}', response_model=JobMessage)
async def get(
        *,
        pk: int,
        service: JobService = Depends(),
):
    """
    get one job by pk
    :param pk:
    :param service:
    :return:
    """
    return {'data': await service.get_by_id(pk=pk)}


@router.post('/jobs', response_model=JobMessage)
async def create(
        *,
        obj_in: JobCreate,
        service: JobService = Depends(),
):
    """
    create job
    :param obj_in:
    :param service:
    :return:
    """
    return {'data': await service.create(obj_in=obj_in)}


@router.patch('/jobs/{pk}', response_model=JobMessage)
async def patch(
        *,
        pk: int,
        obj_in: JobUpdate,
        service: JobService = Depends(),
):
    """
    Update one job's some fields
    :param pk:
    :param service:
    :param obj_in:
    :return:
    """
    return {'data': await service.update_by_id(pk=pk, obj_in=obj_in)}


@router.delete('/jobs/{pk}', response_model=BaseMessage)
async def delete(
        *,
        pk: int,
        service: JobService = Depends(),
):
    """
    Delete one project
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)


@router.get('/jobs/{pk}/_start', response_model=BaseMessage)
async def start(
        *,
        pk: int,
        service: JobService = Depends(),
):
    """
    Run one project
    :param pk:
    :param service:
    :return:
    """
    return await service.start_by_id(pk=pk)


@router.get('/jobs/{pk}/_pause', response_model=BaseMessage)
async def pause(
        *,
        pk: int,
        service: JobService = Depends(),
):
    """
    Run one project
    :param pk:
    :param service:
    :return:
    """
    return await service.pause_by_id(pk=pk)


@router.get('/jobs/{pk}/_unpause', response_model=BaseMessage)
async def unpause(
        *,
        pk: int,
        service: JobService = Depends(),
):
    """
    Run one project
    :param pk:
    :param service:
    :return:
    """
    return await service.unpause_by_id(pk=pk)


@router.get('/jobs/{pk}/_stop', response_model=BaseMessage)
async def stop(
        *,
        pk: int,
        service: JobService = Depends(),
):
    """
    Stop one project
    :param pk:
    :param service:
    :return:
    """
    return await service.stop_by_id(pk=pk)


@router.get('/jobs/{pk}/artifacts', response_model=ArtifactMessage)
async def get_artifact_from_job_id(
        *,
        pk: int,
        service: JobService = Depends(),
):
    """
    get artifact from job_id
    :param pk:
    :param service:
    :return:
    """

    return {'data': await service.get_artifact_from_job_id(pk)}


@router.get('/jobs/{pk}/storage_servers', response_model=StorageServerMessage)
async def get_storage_server_from_job_id(
        *,
        pk: int,
        service: JobService = Depends(),
):
    """
    get storage_server from job_id
    :param pk:
    :param service:
    :return:
    """

    return {'data': await service.get_artifact_from_job_id(pk)}
