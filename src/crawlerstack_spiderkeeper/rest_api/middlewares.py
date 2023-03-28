"""
Api middleware.
"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette_exporter import PrometheusMiddleware

from crawlerstack_spiderkeeper.config import settings


def init_middleware(app: FastAPI):
    """
    Init middleware
    :param app:
    :return:
    """
    # app.add_middleware(BaseHTTPMiddleware, dispatch=db_session_middleware)
    app.add_middleware(PrometheusMiddleware)

    if settings.CORS_ORIGINS and len(settings.CORS_ORIGINS) > 0:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=['x-total-count'],
        )
