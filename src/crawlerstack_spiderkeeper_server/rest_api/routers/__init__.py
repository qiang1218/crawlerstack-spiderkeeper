"""
Router.
"""
from fastapi import APIRouter, FastAPI

from crawlerstack_spiderkeeper_server.config import settings
from crawlerstack_spiderkeeper_server.rest_api.routers import (artifact,
                                                               executor, job,
                                                               project,
                                                               storage_server,
                                                               task,
                                                               task_detail)


def router_v1():
    """
    api v1
    :return:
    """
    router = APIRouter()
    router.include_router(project.router, tags=['project'])
    router.include_router(artifact.router, tags=['artifact'])
    router.include_router(storage_server.router, tags=['storage_server'])
    router.include_router(job.router, tags=['job'])
    router.include_router(task.router, tags=['task'])
    router.include_router(task_detail.router, tags=['task_detail'])
    router.include_router(executor.router, tags=['executor'])
    return router


def init_router(app: FastAPI):
    """
    Init router.
    :param app:
    :return:
    """
    app.include_router(router_v1(), prefix=settings.ROUTER_PREFIX)
