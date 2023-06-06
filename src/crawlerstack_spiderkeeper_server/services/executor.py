"""Executor"""
from crawlerstack_spiderkeeper_server.config import settings
from crawlerstack_spiderkeeper_server.utils.request import RequestWithHttpx


class ExecutorService:
    """
    Executor service.
    """

    @property
    def request_session(self):
        """Request"""
        return RequestWithHttpx()

    @property
    def executor_url(self):
        """Executor url"""
        return settings.SCHEDULER_URL + settings.SCHEDULER_EXECUTOR

    # 仅进行调度器中executor的get转发
    async def get(self, params: dict, headers: dict, **_):
        """
        Get executors
        :param headers:
        :param params:
        :return:
        """
        return await self.request_session.request('GET', self.executor_url, params=params, headers=headers)
