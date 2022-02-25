# """
# Test docker executor.
# """
# import asyncio
# import logging
# import os
#
# import pytest
#
# from crawlerstack_spiderkeeper.executor.docker import (DockerExecutor,
#                                                        DocketExecuteContext)
# from crawlerstack_spiderkeeper.signals import server_stop
#
#
# class TestDockerExecutor:
#     """Test docker executor."""
#
#     @pytest.fixture()
#     async def image(self, artifact_metadata, server_start_signal):
#         """fixture image."""
#         ctx = DocketExecuteContext(artifact_metadata)
#         await ctx.build()
#         yield
#         await ctx.delete()
#
#     @pytest.fixture()
#     async def executor(self, artifact_metadata, image):
#         """Fixture executor."""
#         executor = await DockerExecutor.run(
#             artifact_metadata,
#             cmdline=['python', '-c', 'for i in range(100): print(i); import time;time.sleep(0.01)'],
#             env={'A': 'A'},
#         )
#         yield executor
#         container = await executor.container
#         await container.delete(force=True)
#
#     @pytest.mark.asyncio
#     @pytest.mark.integration
#     async def test(self, artifact_metadata, server_start_signal):   # pylint: disable=unused-argument
#         """Test."""
#         executor = await DockerExecutor.run(
#             artifact_metadata,
#             cmdline=[
#                 'python',
#                 '-c',
#                 'for i in range(10000):import logging;logging.error(i);import time;time.sleep(0.1)'
#             ],
#             env={'A': 'A'},
#         )
#         await asyncio.sleep(1)
#
#         # ##############################
#         count = 0
#         async for _ in executor.log():
#             count += 1
#
#         assert count
#
#         # ##############################
#         count = 0
#
#         async def follow():
#             async for _ in executor.log(follow=True):
#                 nonlocal count
#                 count += 1
#
#         loop = asyncio.get_running_loop()
#         task = loop.create_task(follow())
#         await asyncio.sleep(1)
#         task.cancel()
#         assert count
#
#         # ##############################
#         running = await executor.running()
#         assert running
#
#         # ##############################
#         await executor.stop()
#
#         # ##############################
#         running = await executor.running()
#         assert not running
#
#         await executor.delete()
#         await asyncio.sleep(0.5)
#         await executor.context.delete()
#
#
# class TestDocketExecuteContext:
#     """Test docker execute context."""
#
#     @pytest.fixture()
#     async def ctx(self, artifact_metadata, signal_send):
#         """Fixture Execute context."""
#         ctx = DocketExecuteContext(artifact_metadata)
#         yield ctx
#         await signal_send(server_stop)
#
#     @pytest.mark.integration
#     @pytest.mark.asyncio
#     async def test__make_docker_tar(self, ctx):
#         """Fixture docker tar file."""
#         async with ctx._make_docker_tar() as tarfile:  # pylint: disable=protected-access
#             assert os.path.exists(tarfile)
#             assert tarfile.endswith('.tar.gz')
#
#     @pytest.mark.integration
#     @pytest.mark.asyncio
#     async def test_build_and_delete(self, ctx):
#         """Test build and delete context."""
#         await ctx.build()
#         exist = await ctx.exist()
#         assert exist
#         await ctx.delete()
#         exist = await ctx.exist()
#         assert not exist
#
#     @pytest.mark.integration
#     @pytest.mark.asyncio
#     async def test_delete(self, ctx, caplog):
#         """Test delete context."""
#         with caplog.at_level(logging.DEBUG):
#             await ctx.delete()
#             assert 'not found, skip' in caplog.text
#
#     @pytest.mark.integration
#     @pytest.mark.asyncio
#     async def test_exist(self, ctx):
#         """Test if context exist."""
#         exist = await ctx.exist()
#         assert not exist
