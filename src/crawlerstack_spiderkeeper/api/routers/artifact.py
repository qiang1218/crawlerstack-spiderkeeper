"""
Artifact route.
"""
from typing import List

from fastapi import APIRouter, Body, Depends, File, Response, UploadFile

from crawlerstack_spiderkeeper.api.route_class import AuditRoute
from crawlerstack_spiderkeeper.schemas.artifact import (Artifact,
                                                        ArtifactCreate,
                                                        ArtifactUpdate)
from crawlerstack_spiderkeeper.services import (artifact_file_service,
                                                artifact_service)
from crawlerstack_spiderkeeper.utils import CommonQueryParams

router = APIRouter(route_class=AuditRoute)


@router.get('/artifacts', response_model=List[Artifact])
async def get_multi(
        *,
        response: Response,
        commons: CommonQueryParams = Depends(),
):
    """
    Get artifacts
    :param response:
    :param commons:
    :return:
    """
    total_count = await artifact_service.count()
    # Set total count to header
    response.headers['X-Total-Count'] = str(total_count)
    data = []
    # If no data, we did not execute select op.
    if total_count:
        data = await artifact_service.get_multi(
            skip=commons.skip,
            limit=commons.limit,
            order=commons.order,
            sort=commons.sort
        )
    return data


@router.get('/projects/{project_id}/artifacts', response_model=List[Artifact])
async def get_project_of_artifacts(
        *,
        project_id: int,
):
    """
    Get project of artifacts
    :param project_id:
    :return:
    """
    return await artifact_service.get_project_of_artifacts(project_id=project_id)


@router.get('/artifacts/{pk}', response_model=Artifact)
async def get(
        *,
        pk: int,
):
    """
    Get one artifact by pk
    :param pk:
    :return:
    """
    return await artifact_service.get(pk=pk)


@router.post('/artifacts', response_model=Artifact)
async def create(
        *,
        artifact_in: ArtifactCreate,
):
    """
    Create artifact
    :param artifact_in:
    :return:
    """
    return await artifact_service.create(obj_in=artifact_in)


@router.post('/artifacts/files')
async def upload_artifact(
        *,
        project_id: int = Body(...),
        file: UploadFile = File(...)
):
    """
    Upload artifact file
    :param project_id:
    :param file:
    :return:
    """
    filename = await artifact_file_service.create(project_id, file)
    return {'id': project_id, 'filename': filename}


@router.delete('/artifacts/files/{filename}')
async def delete_artifact(
        *,
        filename: str,
):
    """
    Delete artifact file.
    :param filename:
    :return:
    """
    await artifact_file_service.delete(filename)


@router.put('/artifacts/{pk}', response_model=Artifact)
async def put(
        *,
        pk: int,
        artifact_in: ArtifactUpdate,
):
    """
    Update one artifact's some fields
    :param pk:
    :param artifact_in:
    :return:
    """
    return await artifact_service.update(pk=pk, obj_in=artifact_in)


@router.delete('/artifacts/{pk}', response_model=Artifact)
async def delete(
        *,
        pk: int,
):
    """
    Delete one artifact
    :param pk:
    :return:
    """
    return await artifact_service.delete(pk=pk)
