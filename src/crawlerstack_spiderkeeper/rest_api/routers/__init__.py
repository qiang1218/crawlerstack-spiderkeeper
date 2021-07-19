"""
Router.
"""
from fastapi import APIRouter, FastAPI
from starlette_exporter import handle_metrics

from crawlerstack_spiderkeeper.rest_api.routers import (artifact, audit, job,
                                                        metric, project, server,
                                                        storage, task)


def router_v1():
    """
    api v1
    :return:
    """
    router = APIRouter()

    router.include_router(project.router, prefix='/project', tags=["Project"])
    router.include_router(artifact.router, prefix='/artifact', tags=['Artifact'])
    router.include_router(job.router, prefix='/job', tags=["Job"])
    router.include_router(task.router, prefix='/task', tags=["Task"])
    router.include_router(server.router, prefix='/server', tags=['Server'])

    router.include_router(audit.router, prefix='/audit', tags=['Audit'])

    # router.include_router(log.router, tags=["Log"])
    router.include_router(metric.router, prefix='/metric', tags=["Metric"])
    router.include_router(storage.router, prefix='/storage', tags=["Storage"])

    return router


def init_router(app: FastAPI):
    """
    Init router.
    :param app:
    :return:
    """
    app.add_route("/metrics", handle_metrics)
    app.include_router(router_v1(), prefix='/api/v1')
