"""
Api middleware.
"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from fastapi_sa.middleware import DBSessionMiddleware

from crawlerstack_spiderkeeper_scheduler.config import settings


def init_middleware(app: FastAPI):
    """
    Init middleware
    :param app:
    :return:
    """
    # 数据库session
    app.add_middleware(DBSessionMiddleware)
    # cors
    if settings.CORS_ORIGINS and len(settings.CORS_ORIGINS) > 0:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
