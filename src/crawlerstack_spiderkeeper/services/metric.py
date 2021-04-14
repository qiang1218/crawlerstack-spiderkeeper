"""
Metric service.
"""

import asyncio
from typing import Any, Dict, Optional

from kombu import Message
from prometheus_client import Histogram

from crawlerstack_spiderkeeper.services.base import KombuMixin
from crawlerstack_spiderkeeper.utils import AppId

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

labels = (
    'job_id',
    'task_id',
)


class MetricService(KombuMixin):
    """
    监控服务用来接收爬虫程序自身的监控数据。然后将数据写入 Prometheus 中，外部可以直接使用
    Prometheus 获取系统监控指标，其中会包含爬虫程序的监控数据。
    """
    name = 'metric'

    metrics = {name: Histogram(name, name, labels) for name in metric_name}

    def __init__(self):
        super().__init__()
        self.__should_stop: Optional[asyncio.Future] = None

    async def server_start(self):
        """
        # TODO change method name.
        Start server
        :return:
        """
        await super().server_start()
        self.__should_stop = asyncio.Future()
        # 系统启动后开启监控数据消费任务
        loop = asyncio.get_running_loop()
        loop.create_task(self.consume(
            queue_name=self.queue_name(),
            routing_key=self.routing_key(),
            register_callbacks=[self.consume_on_response],
            should_stop=self.__should_stop
        ))

    async def server_stop(self):
        """
        # TODO change method name.
        Stop server
        :return:
        """
        await super().server_stop()
        if self.__should_stop and not self.__should_stop.done():
            self.__should_stop.set_result(True)
            self.__should_stop = None

    def queue_name(self, app_id: Optional[AppId] = None):
        """
        Queue name.
        :param app_id:
        :return:
        """
        return self.name

    def routing_key(self, app_id: Optional[AppId] = None):
        """Routing key."""
        return self.name

    def consume_on_response(self, body: Dict, message: Message):
        """
        Consume message.
        :param body:
        :param message:
        :return:
        """

        app_id = AppId.from_str(body.get('app_id'))
        self.set_metric(job_id=app_id.job_id, task_id=app_id.task_id, data=body.get('data'))
        message.ack()

    def set_metric(self, job_id: int, task_id: int, data: Dict[str, Any]):
        """
        Set metric.
        :param job_id:
        :param task_id:
        :param data:
        :return:
        """
        try:
            for name, value in data.items():
                metric: Histogram = self.metrics.get(name)
                if metric:
                    metric.labels(job_id, task_id).observe(value)
        except Exception as ex:  # pylint: disable=broad-except
            self.logger.warning(
                'Metric job: %s, task: %s data parser error. data: %s. %s',
                job_id,
                task_id,
                data,
                ex
            )
