"""
FastAPI handler
"""
from fastapi import FastAPI

from crawlerstack_spiderkeeper_server.rest_api.handler import \
    exception_handlers as exh
from crawlerstack_spiderkeeper_server.utils import exceptions as exs


def init_exception_handler(app: FastAPI):
    """
    Init exception handler.
    :param app:
    :return:
    """
    # 多对应关系
    exceptions = [
        exs.SpiderkeeperError,
        exs.ObjectDoesNotExist,
        exs.UnprocessableEntityError,
        exs.DeleteConstraintError,
        exs.CreateConnectionError,
        exs.JobStoppedError,
        exs.JobRunError,
        exs.JobPauseError,
        exs.JobUnpauseError,
        exs.TaskActionError,
    ]

    handler_exceptions = [
        exh.spiderkeeper_exception_handler,
        exh.object_does_not_exist_handler,
        exh.unprocessable_entity_error_handler,
        exh.delete_connection_error_handler,
        exh.create_connection_error_handler,
        exh.job_stopped_error_handler,
        exh.job_run_error_handler,
        exh.job_pause_error_handler,
        exh.job_unpause_error_handler,
        exh.task_action_handler,
    ]

    for k, v in dict(zip(exceptions, handler_exceptions)).items():
        app.add_exception_handler(
            exc_class_or_status_code=k,
            handler=v
        )
