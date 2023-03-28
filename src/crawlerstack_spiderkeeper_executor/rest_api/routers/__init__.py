"""
Router.
"""
from fastapi import APIRouter, FastAPI

from crawlerstack_spiderkeeper_executor.rest_api.routers import executor


def router_v1():
    """
    api v1
    :return:
    """
    router = APIRouter()
    router.include_router(executor.router, tags=['executor'])
    return router


def init_router(app: FastAPI):
    """
    Init router.
    :param app:
    :return:
    """
    app.include_router(router_v1(), prefix='/api/v1')
