"""
Artifact route.
"""
from typing import Optional

from fastapi import APIRouter, Body, Depends, File, Response, UploadFile
from pydantic import BaseModel

from crawlerstack_spiderkeeper.rest_api.route_class import AuditRoute
from crawlerstack_spiderkeeper.rest_api.utils import (auto_commit,
                                                      service_depend)
from crawlerstack_spiderkeeper.schemas.artifact import (Artifact,
                                                        ArtifactCreate,
                                                        ArtifactUpdate, ArtifactFileCreate)
from crawlerstack_spiderkeeper.services import (ArtifactFileService,
                                                ArtifactService)

router = APIRouter(route_class=AuditRoute)


@router.get('/artifacts', response_model=list[Artifact])
async def get(
        *,
        response: Response,
        service: service_depend(ArtifactService) = Depends(),
):
    """
    Get artifacts
    :param response:
    :param service:
    :return:
    """
    total_count = await service.count()
    response.headers['X-Total-Count'] = str(total_count)
    data = []
    if total_count:
        data = await service.get()
    return data


@router.get('/artifacts/{pk}', response_model=Artifact)
async def get(
        *,
        pk: int,
        service: service_depend(ArtifactService) = Depends(),
):
    """
    Get one artifact by pk
    :param service:
    :param pk:
    :return:
    """
    return await service.get_by_id(pk=pk)


@router.post('/artifacts', response_model=Artifact)
@auto_commit
async def create(
        *,
        project_id: int = Body(...),
        file: UploadFile = File(...),
        interpreter: Optional[str] = Body(...),
        execute_path: Optional[str] = Body(...),
        service: service_depend(ArtifactService) = Depends(),
):
    """
    Create artifact
    :param project_id:
    :param interpreter:
    :param execute_path:
    :param file: File
    :param service:
    :return:
    """
    return await service.create(
        obj_in=ArtifactFileCreate(
            project_id=project_id,
            file=file,
            interpreter=interpreter,
            execute_path=execute_path
        ))


@router.post('/artifacts/files')
@auto_commit
async def upload_artifact(
        *,
        project_id: int = Body(...),
        file: UploadFile = File(...),
        service: service_depend(ArtifactFileService) = Depends(),
):
    """
    Upload artifact file
    :param service:
    :param project_id:
    :param file:
    :return:
    """
    filename = await service.create_file(project_id, file)
    return {'id': project_id, 'filename': filename}


@router.delete('/artifacts/files/{filename}')
@auto_commit
async def delete_artifact(
        *,
        filename: str,
        service: service_depend(ArtifactFileService) = Depends(),
):
    """
    Delete artifact file.
    :param service:
    :param filename:
    :return:
    """
    await service.delete_file(filename)


@router.put('/artifacts/{pk}', response_model=Artifact)
@auto_commit
async def put(
        *,
        pk: int,
        artifact_in: ArtifactUpdate,
        service: service_depend(ArtifactService) = Depends(),
):
    """
    Update one artifact's some fields
    :param service:
    :param pk:
    :param artifact_in:
    :return:
    """
    return await service.update_by_id(pk=pk, obj_in=artifact_in)


@router.delete('/artifacts/{pk}', response_model=Artifact)
@auto_commit
async def delete(
        *,
        pk: int,
        service: service_depend(ArtifactService) = Depends(),
):
    """
    Delete one artifact
    :param service:
    :param pk:
    :return:
    """
    return await service.delete_by_id(pk=pk)
