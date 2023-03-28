"""
Customs FastAPI exception handlers

Handle customs exception, and return some http status_code.
"""
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from crawlerstack_spiderkeeper_forwarder.utils.exceptions import (
    DeleteConstraintError, ObjectDoesNotExist, RemoteTaskRunError,
    RequestError, SpiderkeeperError, UnprocessableEntityError)


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


async def delete_constraint_error_handler(request: Request, ex: DeleteConstraintError):
    """
    Handle DeleteConstraintError with http code 406
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content={'detail': ex.detail}
    )


async def request_error_handler(request: Request, ex: RequestError):
    """
    Handle RequestError with http code 400
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': ex.detail}
    )


async def remote_task_run_error_handler(request: Request, ex: RemoteTaskRunError):
    """
    Handle RemoteTaskRunError with http code 400
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': ex.detail}
    )
