"""test docker"""
# import asyncio
#
# import pytest
#
# from crawlerstack_spiderkeeper_executor.executor import DockerExecutor
# from crawlerstack_spiderkeeper_executor.schemas.base import (ExecutorSchema,
#                                                              SpiderSchema,
#                                                              TaskSchema)
#
#
# class TestDockerExecutor:
#     """test docker executor"""
#
#     @pytest.fixture
#     def executor(self, settings):
#         """docker executor fixture"""
#         return DockerExecutor(settings)
#
#     @pytest.fixture
#     def task_params(self):
#         """task params fixture"""
#         return TaskSchema(spider_params=SpiderSchema(
#             DATA_URL='data_url',
#             LOG_URL='log_url',
#             METRICS='metrics',
#             STORAGE_ENABLE=False,
#             TASK_NAME='test_task_name'
#         ),
#             executor_params=ExecutorSchema(
#                 image='python:3.10',
#                 cmdline="['python','-c', 'for i in range(100):import logging;"
#                         "logging.error(i);import time;time.sleep(0.1)']",
#                 volume=None,
#                 environment=None
#             ))
#
#     async def test(self, executor, task_params):
#         """test"""
#
#         container_id = await executor.run(obj_in=task_params)
#         await asyncio.sleep(1)
#
#         status = await executor.status(container_id)
#         assert status == 'running'
#         await asyncio.sleep(12)
#
#         status = await executor.status(container_id)
#         assert status == 'exited'
#
#         await executor.stop(container_id)
#         await asyncio.sleep(1)
#
#         await executor.delete(container_id)
#         await asyncio.sleep(1)
#
#         await executor.client.close()
#
#     @pytest.mark.parametrize(
#         'command, expect_value',
#         [
#             ('["python", "main.py"]', ['python', 'main.py']),
#             (['python', 'main.py'], ['python', 'main.py']),
#             ('test', 'test')
#         ]
#     )
#     def test_format_command(self, executor, command, expect_value):
#         """test format command"""
#         result = executor.format_command(command)
#         assert result == expect_value
