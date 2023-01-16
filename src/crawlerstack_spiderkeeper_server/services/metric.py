"""metric"""
import logging
from typing import Any

from prometheus_client import Histogram

from crawlerstack_spiderkeeper_server.services.base import ICRUD

logger = logging.getLogger(__name__)

metric_name = [
    'downloader_request_count',
    'downloader_request_bytes',
    'downloader_request_method_count_GET',
    'downloader_response_count',
    'downloader_response_status_count_200',
    'downloader_response_status_count_301',
    'downloader_response_status_count_302',
    'downloader_response_bytes',
    'downloader_exception_count',
]

labels = ('Job_id', 'Task_name')

metrics = {name: Histogram(name, name, labels) for name in metric_name}


class MetricService(ICRUD):
    """Metric service"""

    async def get(self, task_name):
        """Get metric from prometheus with task_name"""

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
        将数据写入 prometheus 指标
        :param task_name:
        :param data:
        :return:
        """
        job_id = task_name.split('-')[0]
        try:
            for name, value in data.items():
                metric: Histogram = metrics.get(name)
                if metric:
                    metric.labels(job_id, task_name).observe(value)
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning(
                'Metric task: %s data parser error. data: %s. %s',
                task_name,
                data,
                ex
            )
