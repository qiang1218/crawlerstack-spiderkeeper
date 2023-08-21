"""log"""
from typing import Any

from opentelemetry.sdk._logs import LogRecord  # noqa

from crawlerstack_spiderkeeper_server.config import settings
from crawlerstack_spiderkeeper_server.schemas.otel_log import LogRecordSchema
from crawlerstack_spiderkeeper_server.services.base import ICRUD
from crawlerstack_spiderkeeper_server.utils.otel import log_provider, resource

otel_logger = log_provider.get_logger(settings.SERVICE_NAME)


class LogService(ICRUD):
    """Log service"""

    async def get(self, *args, **kwargs) -> Any:
        """Get"""

    @staticmethod
    def upload_data(data: str, job_id: str, task_name: str, task_time: int):
        """Upload data"""
        record = LogRecord(
            **LogRecordSchema(
                body=data,
                attributes={'task_name': task_name,
                            'job_id': job_id,
                            'task_time': task_time
                            }).dict(),
            resource=resource
        )
        otel_logger.emit(record)

    async def create(self, data: dict) -> None:
        """Create log by task name"""
        task_name = data.get('task_name')
        job_id, _, task_time = task_name.split('-')
        datas = data.get('data')
        for row in datas:
            self.upload_data(row, job_id=job_id, task_name=task_name, task_time=task_time)

    async def update(self, *args, **kwargs) -> Any:
        """Update"""

    async def delete(self, *args, **kwargs) -> Any:
        """Delete"""
