"""test manage"""
import asyncio

import pytest

from crawlerstack_spiderkeeper_scheduler.manage import SpiderKeeperScheduler

#
# @pytest.fixture
# def scheduler(settings):
#     return SpiderKeeperScheduler(settings)
#
#
# async def task():
#     await asyncio.sleep(1)
#     print('1')
#
#
# async def test_start(scheduler):
#     """test start"""
#     scheduler.rest_api.init()
#     scheduler.scheduler.start()
#     scheduler.scheduler.apscheduler.add_job(task, trigger='interval', seconds=2)
#     for i in range(15):
#         await asyncio.sleep(1)