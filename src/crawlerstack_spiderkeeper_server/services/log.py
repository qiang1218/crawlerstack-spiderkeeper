"""log"""
import logging
from pathlib import Path
from typing import Any, List

from crawlerstack_spiderkeeper_server.config import local_path, settings
from crawlerstack_spiderkeeper_server.services.base import ICRUD
from crawlerstack_spiderkeeper_server.utils import File

logger = logging.getLogger(__name__)


class LogService(ICRUD):
    """Log service"""

    @staticmethod
    def gen_log_path_str(task_name: str) -> Path:
        """
        Gen log path str with task name

        task_name: job_id-trigger_type-datetime_str
        example: 2-manual-20191215152202
        2-scheduled-20191215152202
        :param task_name:
        :return:
        """
        task_name += settings.LOG_TASK_PATH_SUFFIX
        return Path(local_path, settings.LOG_TASK_PATH_PREFIX, *task_name.split(settings.LOG_TASK_PATH_SEPARATOR))

    async def get(self, query: dict) -> List[str]:
        """
        Get log by task name
        :param query:
        :return:
        """
        filename = self.gen_log_path_str(query.get('task_name'))
        rows = query.get('rows')
        try:
            return await File(filename).last(line=rows)
        except FileNotFoundError as ex:
            logger.error('No such file or directory, filename: %s', filename)
            logger.error('%s', ex)

    async def create(self, data: dict) -> None:
        """Create log by task name"""
        task_name = data.get('task_name')
        filename = self.gen_log_path_str(task_name)
        await File(filename).write(datas=data.get('data'))

    async def update(self, *args, **kwargs) -> Any:
        """Update"""

    async def delete(self, *args, **kwargs) -> Any:
        """Delete"""
