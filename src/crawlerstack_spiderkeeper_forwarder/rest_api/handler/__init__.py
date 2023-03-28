"""
FastAPI handler
"""
from fastapi import FastAPI

from crawlerstack_spiderkeeper_forwarder.rest_api.handler import \
    exception_handlers as exh
from crawlerstack_spiderkeeper_forwarder.utils import exceptions as exs


def init_exception_handler(app: FastAPI):
    """
    Init exception handler.
    :param app:
    :return:
    """
    exceptions = [
        exs.SpiderkeeperError,
        exs.ObjectDoesNotExist,
        exs.UnprocessableEntityError,
        exs.DeleteConstraintError,
        exs.RequestError,
        exs.RemoteTaskRunError,
    ]

    handler_exceptions = [
        exh.spiderkeeper_exception_handler,
        exh.object_does_not_exist_handler,
        exh.unprocessable_entity_error_handler,
        exh.delete_constraint_error_handler,
        exh.request_error_handler,
        exh.remote_task_run_error_handler,
    ]

    for k, v in dict(zip(exceptions, handler_exceptions)).items():
        app.add_exception_handler(
            exc_class_or_status_code=k,
            handler=v
        )
