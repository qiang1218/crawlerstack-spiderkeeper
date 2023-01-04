"""
Router.
"""
from fastapi import APIRouter, FastAPI

from crawlerstack_spiderkeeper_scheduler.rest_api.routers import (executor, executor_detail, job, task, heartbeat)


def router_v1():
    """
    api v1
    :return:
    """
    router = APIRouter()
    router.include_router(executor.router, tags=['executor'])
    router.include_router(executor_detail.router, tags=['executor_detail'])
    router.include_router(job.router, tags=['job'])
    router.include_router(task.router, tags=['task'])
    router.include_router(heartbeat.router, tags=['heartbeat'])
    return router


def init_router(app: FastAPI):
    """
    Init router.
    :param app:
    :return:
    """
    app.include_router(router_v1(), prefix='/api/v1')
