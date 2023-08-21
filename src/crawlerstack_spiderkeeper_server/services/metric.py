"""metric"""
import logging
from typing import Any

from crawlerstack_spiderkeeper_server.config import settings
from crawlerstack_spiderkeeper_server.services.base import ICRUD
from crawlerstack_spiderkeeper_server.utils.otel import meter_provider

logger = logging.getLogger(__name__)

labels = ('Job_id', 'Task_name', 'Category')
metrics = {}
meter = meter_provider.get_meter(settings.SERVICE_NAME)


class MetricService(ICRUD):
    """Metric service"""

    async def get(self, task_name):
        """Get"""

    async def create(self, data: dict) -> None:
        """Create metric by task name"""
        task_name = data.get('task_name')
        self.set_metric(task_name=task_name, data=data.get('data'))

    async def update(self, *args, **kwargs) -> Any:
        """Update"""

    async def delete(self, *args, **kwargs) -> Any:
        """Delete"""

    @staticmethod
    def set_metric(task_name: str, data: dict[str, Any]):
        """
        将数据写入 otel 指标
        :param task_name:
        :param data:
        :return:
        """
        job_id = task_name.split('-')[0]
        try:
            for name, value in data.items():
                if name.startswith('spiderkeeper_'):
                    # 初始化后动态添加
                    metric = metrics.get(name) if name in metrics \
                        else metrics.setdefault(name,
                                                meter.create_histogram(name=name, description=name))
                    category = name.split('_')[1]
                    if metric:
                        metric.record(value,
                                      attributes={
                                          'job_id': job_id,
                                          'task_name': task_name,
                                          'category': category
                                      })
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning(
                'Metric task: %s data parser error. data: %s. %s',
                task_name,
                data,
                ex
            )
