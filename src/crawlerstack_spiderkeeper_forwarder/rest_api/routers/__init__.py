"""
Router.
"""
from fastapi import APIRouter, FastAPI

from crawlerstack_spiderkeeper_forwarder.rest_api.routers import (data, log,
                                                                  metric)


def router_v1():
    """
    api v1
    :return:
    """
    router = APIRouter()
    router.include_router(data.router, tags=['data'])
    router.include_router(log.router, tags=['log'])
    router.include_router(metric.router, tags=['metric'])

    return router


def init_router(app: FastAPI):
    """
    Init router.
    :param app:
    :return:
    """
    app.include_router(router_v1(), prefix='/api/v1')
