"""
Metric service.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from kombu import Message
from prometheus_client import Histogram

from crawlerstack_spiderkeeper.services.base import ServerEventMixin, ICRUD
from crawlerstack_spiderkeeper.services.utils import Kombu
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils import AppId, AppData

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

logger = logging.getLogger(__name__)


class MetricKombu(Kombu):
    NAME = 'metric'


class MetricService(ICRUD, ServerEventMixin):
    """
    用来将监控数据写入 prometheus 中，通过接口进行访问获取
    prometheus 监控主机。
    """

    metrics = {name: Histogram(name, name, labels) for name in metric_name}
    kombu = MetricKombu()

    __should_stop: Optional[asyncio.Future] = None

    def get(self, *args, **kwargs) -> Any:
        pass

    async def create(self, app_data: AppData) -> Any:
        await self.kombu.publish(
            queue_name=self.queue_name(),
            routing_key=self.routing_key(),
            body={
                'app_id': str(app_data.app_id),
                'data': app_data.data
            },
        )

    def update(self, *args, **kwargs) -> Any:
        pass

    def delete(self, *args, **kwargs) -> Any:
        pass

    async def server_start(self):
        """
        Start server
        :return:
        """
        await self.kombu.server_start()
        self.__should_stop = asyncio.Future()
        # 系统启动后开启监控数据消费任务
        loop = asyncio.get_running_loop()
        loop.create_task(self.kombu.consume(
            queue_name=self.queue_name(),
            routing_key=self.routing_key(),
            register_callbacks=[self.consume_on_response],
            should_stop=self.__should_stop
        ))

    async def server_stop(self):
        """
        Stop server
        :return:
        """
        await self.kombu.server_stop()
        if self.__should_stop and not self.__should_stop.done():
            self.__should_stop.set_result(True)
            self.__should_stop = None

    def queue_name(self):
        """Queue name."""
        return self.kombu.name

    def routing_key(self):
        """Routing key."""
        return self.kombu.name

    def consume_on_response(self, body: Dict, message: Message):
        """
        消费数据，并将数据写入监控指标中。
        :param body:
        :param message:
        :return:
        """
        print('=' * 20)
        print(body)
        app_id = AppId.from_str(body.get('app_id'))
        self.set_metric(job_id=app_id.job_id, task_id=app_id.task_id, data=body.get('data'))
        message.ack()

    def set_metric(self, job_id: int, task_id: int, data: Dict[str, Any]):
        """
        将数据写入 prometheus 指标
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
            logger.warning(
                'Metric job: %s, task: %s data parser error. data: %s. %s',
                job_id,
                task_id,
                data,
                ex
            )


# 注册事件
server_start.connect(MetricService.server_start_event)
server_stop.connect(MetricService.server_stop_event)
