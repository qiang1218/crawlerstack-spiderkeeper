"""
Api middleware.
"""
from fastapi import FastAPI
from fastapi_sa.middleware import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette_exporter import PrometheusMiddleware

from crawlerstack_spiderkeeper_server.config import settings


def init_middleware(app: FastAPI):
    """
    Init middleware
    :param app:
    :return:
    """
    # 监控
    app.add_middleware(PrometheusMiddleware)
    # cors
    if settings.CORS_ORIGINS and len(settings.CORS_ORIGINS) > 0:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    # 数据库session
    app.add_middleware(DBSessionMiddleware)
