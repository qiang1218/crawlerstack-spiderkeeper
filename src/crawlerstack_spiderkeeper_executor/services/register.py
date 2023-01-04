"""register"""
import time

from crawlerstack_spiderkeeper_executor.utils import SingletonMeta
from crawlerstack_spiderkeeper_executor.utils.request import RequestWithSession

from crawlerstack_spiderkeeper_executor.utils.status import Status


class RegisterService(metaclass=SingletonMeta):
    """Register service"""

    def __init__(self, settings, **kwargs):
        """
        init
        :param settings:
        :param kwargs:
        """
        self.settings = settings
        self.local_url = self.settings.LOCAL_URL
        self.executor_type = self.settings.EXECUTOR_TYPE
        self.executor_remote_url = self.settings.EXECUTOR_REMOTE_URL
        self.executor_name = self.settings.EXECUTOR_NAME
        self.executor_selector = self.settings.EXECUTOR_SELECTOR

        self.heartbeat_interval = self.settings.HEARTBEAT_INTERVAL
        self.heartbeat_url = self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_HEARTBEATS_SUFFIX
        self.register_url = self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_EXECUTOR_CREATE_SUFFIX

    @property
    def request_session(self):
        return RequestWithSession()

    def register(self) -> int:
        """
        register
        :return:
        """
        resp = self.request_session.request('POST', self.register_url, json=self.register_params)
        executor_id = resp.get('data', {}).get('executor_id')
        return executor_id

    @property
    def register_params(self) -> dict:
        """
        register params
        :return:
        """
        return {'name': self.executor_name,
                'selector': self.executor_selector,
                'url': self.executor_remote_url,
                'type': self.executor_type}

    def heartbeat_params(self):
        """
        heartbeat params
        :return:
        """
        resource_view = self.resource_view()
        resource_view.setdefault('status', Status.ONLINE.value)
        return resource_view

    @staticmethod
    def resource_view() -> dict:
        """
        resource view
        :return:
        """
        # TODO: 后续实现, 方法为实例方法
        return {'memory': 0, 'cpu': 100}

    def heartbeat(self, executor_id: int):
        """
        heartbeat
        :param executor_id:
        :return:
        """
        # 暂时仅上报心跳，不对其他资源收集处理
        while True:
            self.request_session.request('POST', self.heartbeat_url % executor_id, json=self.heartbeat_params(),
                                         timeout=3)
            time.sleep(self.heartbeat_interval)
