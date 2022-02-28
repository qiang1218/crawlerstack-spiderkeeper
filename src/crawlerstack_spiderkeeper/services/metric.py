"""
Metric service.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from kombu import Message
from prometheus_client import Histogram

from crawlerstack_spiderkeeper.services.base import ICRUD
from crawlerstack_spiderkeeper.services.utils import Kombu
from crawlerstack_spiderkeeper.signals import server_start, server_stop
from crawlerstack_spiderkeeper.utils import AppData, AppId

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


class MetricBackgroundTask:
    """Metric background task"""
    NAME = 'metric'
    kombu = Kombu()

    metrics = {name: Histogram(name, name, labels) for name in metric_name}
    _task: None | asyncio.Task = None
    _should_stop: asyncio.Future = asyncio.Future()

    @classmethod
    async def run_from_cls(cls, **_kwargs):
        """
        运行任务
        :return:
        """
        obj = cls()
        await obj.start()

    @classmethod
    async def stop_from_cls(cls, **_kwargs):
        """
        Stop server
        :return:
        """
        obj = cls()
        await obj.stop()

    @property
    def queue_name(self):
        """Queue name."""
        return self.NAME

    @property
    def routing_key(self):
        """Routing key."""
        return self.NAME

    @property
    def exchange_name(self):
        """Exchange name."""
        return self.NAME

    async def start(self):
        """
        Start server
        :return:
        """
        logger.info('Starting metric task.')
        if self._should_stop.done():
            MetricBackgroundTask._should_stop = asyncio.Future()

        # 系统启动后开启监控数据消费任务
        loop = asyncio.get_running_loop()
        logger.debug('Start consuming metric data from kombu.')
        MetricBackgroundTask._task = loop.create_task(self.kombu.consume(
            queue_name=self.queue_name,
            routing_key=self.routing_key,
            exchange_name=self.exchange_name,
            register_callbacks=[self.consume_on_response],
            should_stop=self._should_stop
        ))
        # task.add_done_callback(functools.partial(setattr, self, '_should_stop', None))

    async def stop(self):
        """
        Stop server
        :return:
        """
        if not self._should_stop.done():
            MetricBackgroundTask._should_stop.set_result('Stop')
            await asyncio.sleep(0)
            if self._task and not self._task.done():
                self._task.cancel()
                logger.debug('Cancel metric task.')
        logger.info('Stopped metric task')

    def consume_on_response(self, body: Dict, message: Message):
        """
        消费数据，并将数据写入监控指标中。
        :param body:
        :param message:
        :return:
        """
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


class MetricService(ICRUD):
    """
    用来将监控数据写入 prometheus 中，通过接口进行访问获取
    prometheus 监控主机。
    """

    kombu = Kombu()
    NAME = 'metric'

    __should_stop: Optional[asyncio.Future] = None

    @property
    def queue_name(self):
        """Queue name."""
        return self.NAME

    @property
    def routing_key(self):
        """Routing key."""
        return self.NAME

    @property
    def exchange_name(self):
        """Exchange name."""
        return self.NAME

    async def get(self, *args, **kwargs) -> Any:
        """获取一条记录。"""
        pass

    async def create(self, app_data: AppData) -> Any:
        """
        创建一条监控记录。

        :param app_data:
        :return:
        """
        body = {
            'app_id': str(app_data.app_id),
            'data': app_data.data
        }

        await self.kombu.publish(
            queue_name=self.queue_name,
            routing_key=self.routing_key,
            exchange_name=self.exchange_name,
            body=body,
        )
        logger.debug(
            f'Publish data <queue_name={self.queue_name}, '
            f'routing_key={self.routing_key},'
            f'exchange_name={self.exchange_name},'
            f'body={body}>'
        )

    async def update(self, *args, **kwargs) -> Any:
        """更新一条记录。。"""
        pass

    async def delete(self, *args, **kwargs) -> Any:
        """删除一条记录。"""
        pass


# # 注册事件
server_start.connect(MetricBackgroundTask.run_from_cls)
server_stop.connect(MetricBackgroundTask.stop_from_cls)
