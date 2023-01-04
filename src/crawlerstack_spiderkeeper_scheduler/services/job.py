"""Job"""
import logging

from crawlerstack_spiderkeeper_scheduler.config import settings
from crawlerstack_spiderkeeper_scheduler.services.scheduler import SchedulerServer

from crawlerstack_spiderkeeper_scheduler.utils.request import RequestWithSession
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


class JobService:
    """
    Job service.
    """

    @property
    def job_url(self):
        return settings.SERVER_URL + settings.SERVER_JOB_SUFFIX

    @property
    def artifact_url(self):
        return settings.SERVER_URL + settings.SERVER_ARTIFACT_SUFFIX

    @property
    def data_url(self):
        return settings.COLLECTOR_BASE_URL + settings.COLLECTOR_DATA_SUFFIX

    @property
    def log_url(self):
        return settings.COLLECTOR_BASE_URL + settings.COLLECTOR_LOG_SUFFIX

    @property
    def metric_url(self):
        return settings.COLLECTOR_BASE_URL + settings.COLLECTOR_METRIC_SUFFIX

    @property
    def scheduler(self):
        return SchedulerServer()

    @property
    def request_session(self):
        return RequestWithSession()

    def start_by_id(self, job_id: str) -> None:
        """Start job_id"""
        # 任务的单次触发
        # 获取任务需要的参数，即调用接口，获取对应调度参数
        # 1 先获取server中job的相关数据
        job = self.request_session.request('GET', self.job_url % job_id).get('data')
        artifact = self.request_session.request('GET', self.artifact_url % job_id).get('data')

        if not (job and artifact):
            raise ObjectDoesNotExist()

        trigger_expression = job.pop('trigger_expression')
        spider_params = self.spider_params(job)
        executor_params = self.executor_params(job, artifact)

        # 任务调用
        return self.scheduler.add_job(job_id, trigger_expression, spider_params=spider_params,
                                      executor_params=executor_params, job_id=job_id)

    def spider_params(self, job: dict) -> dict:
        """
        spider parameters
        :param job:
        :return:
        """
        # 考虑爬虫程序中获取变量，统一大写
        storage_enable = job.get('storage_enable')
        return {'DATA_URL': self.data_url, 'LOG_URL': self.log_url, 'METRICS': self.metric_url,
                'STORAGE_ENABLE': storage_enable}

    @staticmethod
    def executor_params(job: dict, artifact: dict) -> dict:
        """
        executor parameter
        :param job:
        :param artifact:
        :return:
        """
        # 执行器变量，统一小写
        images = artifact.get('image') + (artifact.get('version') if artifact.get('version') else 'latest')
        # cmdline 字符串 如果多个命令字符串 "['','']"
        cmdline = job.get('cmdline', '')
        executor_selector = job.get('executor_selector')
        executor_type = job.get('executor_type')
        # volume ; 切割
        volume = job.get('volume', '').split(';')
        # environment ['FOO=bar', 'BAZ=q']  ;切割
        environment = job.get('environment', '').split(';')

        return {'image_name': images, 'cmdline': cmdline, 'executor_selector': executor_selector,
                'executor_type': executor_type, 'volume': volume, 'environment': environment}

    def stop_by_id(self, job_id: str):
        """Stop job_id"""
        # 结束id对应的所有任务
        self.scheduler.remove_job(job_id)

    def pause_by_id(self, job_id: str):
        """Pause job_id"""
        # 暂停id对应任务，需保证job已经开启
        self.scheduler.pause_job(job_id)

    def unpause_by_id(self, job_id: str):
        """unpause job_id"""
        # 恢复被暂停的任务，需保证job已经开启
        self.scheduler.unpause_job(job_id)
