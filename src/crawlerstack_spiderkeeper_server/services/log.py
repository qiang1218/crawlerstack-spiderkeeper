"""log"""
from pathlib import Path
from typing import List, Any

from crawlerstack_spiderkeeper_server.services.base import ICRUD
from crawlerstack_spiderkeeper_server.utils import File
from crawlerstack_spiderkeeper_server.config import settings, local_path


class LogService(ICRUD):

    @staticmethod
    def gen_log_path_str(task_name: str) -> Path:
        """
        gen log path str with task name

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
        get log by task name
        :param query:
        :return:
        """
        filename = self.gen_log_path_str(query.get('task_name'))
        rows = query.get('rows')
        return await File(filename).last(line=rows)

    async def create(self, data: dict) -> None:
        """create log by task name"""
        task_name = data.get('task_name')
        filename = self.gen_log_path_str(task_name)
        await File(filename).write(datas=data.get('data'))

    async def update(self, *args, **kwargs) -> Any:
        """update"""
        pass

    async def delete(self, *args, **kwargs) -> Any:
        """delete"""
        pass
