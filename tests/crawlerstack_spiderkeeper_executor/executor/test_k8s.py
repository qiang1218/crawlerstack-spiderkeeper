"""Test k8s"""
import pytest

from crawlerstack_spiderkeeper_executor.executor.k8s import K8SExecutor
from crawlerstack_spiderkeeper_executor.schemas.base import (ExecutorSchema,
                                                             SpiderSchema,
                                                             TaskSchema)


class TestK8s:
    """Test k8s"""

    @pytest.fixture
    def k8s(self, settings):
        """K8s fixture"""
        settings.EXECUTOR_TYPE = 'k8s'
        return K8SExecutor(settings)

    @pytest.fixture
    def task_params(self):
        """task params fixture"""
        return TaskSchema(spider_params=SpiderSchema(
            DATA_URL='data_url',
            LOG_URL='log_url',
            METRICS_URL='metrics',
            STORAGE_ENABLE=False,
            SNAPSHOT_ENABLE=False,
            TASK_NAME='test-task-name'
        ),
            executor_params=ExecutorSchema(
                image='python:3.10',
                cmdline=['python', '-c',
                         'for i in range(100):import logging;logging.error(i);import time;time.sleep(2)'],
                volume=['/test:/var/data'],
                environment=None,
                cpu_limit=2000,
                memory_limit=2048,
            ))

    @pytest.mark.skip(reason="Skipping integration tests")
    async def test_run(self, k8s, task_params):
        """
        Test run
        集成测试使用
        :param k8s:
        :param task_params:
        :return:
        """
        # 状态获取
        before_result = await k8s.get()
        # 运行任务
        pod_name = await k8s.run(obj_in=task_params)
        # 判断
        after_result = await k8s.get()
        assert len(after_result) - len(before_result) == 1
        # 删除
        await k8s.delete(pod_name=pod_name)
