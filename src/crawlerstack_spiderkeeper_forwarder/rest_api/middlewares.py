"""
Api middleware.
"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from crawlerstack_spiderkeeper_forwarder.config import settings


def init_middleware(app: FastAPI):
    """
    Init middleware
    :param app:
    :return:
    """
    # cors
    if settings.CORS_ORIGINS and len(settings.CORS_ORIGINS) > 0:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
