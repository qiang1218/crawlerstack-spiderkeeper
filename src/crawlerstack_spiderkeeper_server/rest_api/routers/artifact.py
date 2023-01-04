"""
Artifact route
"""
import logging

from fastapi import APIRouter, Depends

from crawlerstack_spiderkeeper_server.messages.project import ProjectMessage
from crawlerstack_spiderkeeper_server.schemas.artifact import (ArtifactCreate,
                                                               ArtifactUpdate)
from crawlerstack_spiderkeeper_server.services.artifact import ArtifactService

from crawlerstack_spiderkeeper_server.messages.base import BaseMessage
from crawlerstack_spiderkeeper_server.messages.artifact import ArtifactMessage, ArtifactMessages

from crawlerstack_spiderkeeper_server.utils.extractor import query_extractor

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/artifacts", response_model=ArtifactMessages)
async def get_multi(
        *,
        query: dict = Depends(query_extractor),
        service: ArtifactService = Depends(),
):
    """
    Get artifacts
    :param query:
    :param service:
    :return:
    """
    total_count = await service.count(search_fields=query.get('search_fields'))
    data = dict(**query)
    if total_count:
        items = await service.get(**query)
        data.update({'data': items, 'total_count': total_count})
    else:
        data.update({'data': []})
    return data


@router.get('/artifacts/{pk}', response_model=ArtifactMessage)
async def get(
        *,
        pk: int,
        service: ArtifactService = Depends(),
):
    """
    get one artifact by pk
    :param pk:
    :param service:
    :return:
    """
    return {'data': await service.get_by_id(pk=pk)}


@router.post('/artifacts', response_model=ArtifactMessage)
async def create(
        *,
        obj_in: ArtifactCreate,
        service: ArtifactService = Depends(),
):
    """
    create artifact
    :param obj_in:
    :param service:
    :return:
    """
    return {'data': await service.create(obj_in=obj_in)}


@router.patch('/artifacts/{pk}', response_model=ArtifactMessage)
async def patch(
        *,
        pk: int,
        obj_in: ArtifactUpdate,
        service: ArtifactService = Depends(),
):
    """
    Update one artifact's some fields
    :param pk:
    :param service:
    :param obj_in:
    :return:
    """
    return {'data': await service.update_by_id(pk=pk, obj_in=obj_in)}


@router.delete('/artifacts/{pk}', response_model=BaseMessage)
async def delete(
        *,
        pk: int,
        service: ArtifactService = Depends(),
):
    """
    Delete one artifact
    :param pk:
    :param service:
    :return:
    """
    return await service.delete_by_id(pk=pk)


@router.get('/artifacts/{pk}/projects', response_model=ProjectMessage)
async def get_project_from_artifact_id(
        *,
        pk: int,
        service: ArtifactService = Depends(),
):
    """
    get a project from artifact id
    :param pk:
    :param service:
    :return:
    """

    return {'data': await service.get_project_from_artifact_id(pk)}
