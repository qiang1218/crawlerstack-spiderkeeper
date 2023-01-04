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
    # handle spiderkeeper root exception with http code 500
    app.add_exception_handler(
        exc_class_or_status_code=exs.SpiderkeeperError,
        handler=exh.spiderkeeper_exception_handler
    )
    # handle ObjectDoseNotExist with http code 404
    app.add_exception_handler(
        exc_class_or_status_code=exs.ObjectDoesNotExist,
        handler=exh.object_does_not_exist_handler,
    )
    app.add_exception_handler(
        exc_class_or_status_code=exs.UnprocessableEntityError,
        handler=exh.unprocessable_entity_error_handler
    )
