"""
Log api.
"""
# import logging
#
# from fastapi import APIRouter
#
# from crawlerstack_spiderkeeper.schemas import AppData
# from crawlerstack_spiderkeeper.services.log import log
#
# logger = logging.getLogger(__name__)
# router = APIRouter()
#
#
# @router.get('/log')
# async def get(*, app_id: str = None):
#     return await log.get(app_id=app_id)
#
#
# @router.post('/log')
# async def post(
#         *,
#         app_data: AppData
# ):
#     await log.create(app_data)
