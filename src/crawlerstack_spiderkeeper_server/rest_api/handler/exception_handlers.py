"""
Customs FastAPI exception handlers

Handle customs exception, and return some http status_code.
"""
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from crawlerstack_spiderkeeper_server.utils.exceptions import (
    CreateConnectionError, DeleteConstraintError, JobPauseError, JobRunError,
    JobStoppedError, JobUnpauseError, ObjectDoesNotExist, SpiderkeeperError,
    TaskActionError, UnprocessableEntityError)


async def spiderkeeper_exception_handler(request: Request, ex: SpiderkeeperError):
    """
    Handle SpiderKeeperError with http code 500
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': ex.detail}
    )


async def object_does_not_exist_handler(request: Request, ex: ObjectDoesNotExist):
    """
    Handle ObjectDoesNotExist with http code 404
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': ex.detail}
    )


async def unprocessable_entity_error_handler(request: Request, ex: UnprocessableEntityError):
    """
    Handle UnprocessableEntityError with http code 422
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={'detail': ex.detail}
    )


async def create_connection_error_handler(request: Request, ex: CreateConnectionError):
    """
    Handle CreateConnectionError with http code 400
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': ex.detail}
    )


async def delete_connection_error_handler(request: Request, ex: DeleteConstraintError):
    """
    Handle DeleteConstraintError with http code 404
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': ex.detail}
    )


async def job_stopped_error_handler(request: Request, ex: JobStoppedError):
    """
    Handle JobStoppedError with http code 400
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': ex.detail}
    )


async def job_run_error_handler(request: Request, ex: JobRunError):
    """
    Handle JobRunError with http code 400
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': ex.detail}
    )


async def job_pause_error_handler(request: Request, ex: JobPauseError):
    """
    Handle JobPauseError with http code 400
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': ex.detail}
    )


async def job_unpause_error_handler(request: Request, ex: JobUnpauseError):
    """
    Handle JobUnpauseError with http code 400
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': ex.detail}
    )


async def task_action_handler(request: Request, ex: TaskActionError):
    """
    Handle TaskActionError with http code 400
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': ex.detail}
    )
