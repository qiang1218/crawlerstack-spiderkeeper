"""Job"""
import logging

from crawlerstack_spiderkeeper_scheduler.config import settings
from crawlerstack_spiderkeeper_scheduler.services.scheduler import \
    SchedulerServer
from crawlerstack_spiderkeeper_scheduler.tasks.task import task_run
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    ObjectDoesNotExist
from crawlerstack_spiderkeeper_scheduler.utils.request import RequestWithHttpx

logger = logging.getLogger(__name__)


class JobService:
    """
    Job service.
    """

    @property
    def job_url(self):
        """job url"""
        return settings.SERVER_BASE_URL + settings.SERVER_JOB_SUFFIX

    @property
    def artifact_url(self):
        """artifact url"""
        return settings.SERVER_BASE_URL + settings.SERVER_ARTIFACT_SUFFIX

    @property
    def data_url(self):
        """data url"""
        return settings.FORWARDER_BASE_URL + settings.FORWARDER_DATA_SUFFIX

    @property
    def log_url(self):
        """log url"""
        return settings.FORWARDER_BASE_URL + settings.FORWARDER_LOG_SUFFIX

    @property
    def metric_url(self):
        """metric url"""
        return settings.FORWARDER_BASE_URL + settings.FORWARDER_METRIC_SUFFIX

    @property
    def scheduler(self):
        """scheduler"""
        return SchedulerServer(settings)

    @property
    def request_session(self):
        """request session"""
        return RequestWithHttpx()

    async def start_by_id(self, job_id: str) -> dict:
        """Start job_id"""
        # 任务的单次触发
        # 获取任务需要的参数，即调用接口，获取对应调度参数
        # 1 先获取server中job的相关数据
        job = await self.get_job(job_id)
        artifact = await self.get_artifact(job_id)

        if not (job and artifact):
            raise ObjectDoesNotExist()

        trigger_expression = job.pop('trigger_expression')
        spider_params = self.spider_params(job)
        executor_params = self.executor_params(job, artifact)

        # 任务调用
        # todo 后续添加对同一job的更新操作,如果已经存在,则进行更新,不存在则插入,由start接口控制
        try:
            self.scheduler.add_job(task_run,
                                   trigger_expression=trigger_expression,
                                   spider_params=spider_params,
                                   executor_params=executor_params,
                                   job_id=job_id)
        except Exception as ex:
            # 考虑存在重复的任务,目前job_id满足唯一性,多次添加同一个会异常
            logger.error('Add job to scheduler failed, info: %s', ex)
        return {'message': 'success'}

    async def get_job(self, job_id: str):
        """get job data"""
        data = await self.request_session.request('GET', self.job_url % job_id)
        return data.get('data')

    async def get_artifact(self, job_id: str):
        """get artifact data"""
        data = await self.request_session.request('GET', self.artifact_url % job_id)
        return data.get('data')

    def spider_params(self, job: dict) -> dict:
        """
        spider parameters
        :param job:
        :return:
        """
        # 考虑爬虫程序中获取变量，统一大写
        storage_enable = job.get('storage_enable')
        snapshot_enable = job.get('snapshot_enable')
        return {'DATA_URL': self.data_url, 'LOG_URL': self.log_url, 'METRICS_URL': self.metric_url,
                'STORAGE_ENABLE': storage_enable, 'SNAPSHOT_ENABLE': snapshot_enable}

    @staticmethod
    def executor_params(job: dict, artifact: dict) -> dict:
        """
        executor parameter
        :param job:
        :param artifact:
        :return:
        """
        # 执行器变量，统一小写
        images = artifact.get('image') + ':' + (artifact.get('version') if artifact.get('version') else 'latest')
        # cmdline 字符串 空格链接
        cmdline = job.get('cmdline', '')
        executor_selector = job.get('executor_selector')
        executor_type = job.get('executor_type')
        # volume ; 切割
        volume = job.get('volume', '').split(';')
        # environment  字符串 ;切割 ['FOO=bar', 'BAZ=q']
        environment = job.get('environment', '').split(';')

        return {'image': images, 'cmdline': cmdline, 'executor_selector': executor_selector,
                'executor_type': executor_type, 'volume': volume, 'environment': environment}

    async def stop_by_id(self, job_id: str) -> dict:
        """Stop job_id"""
        # 结束id对应的所有任务
        self.scheduler.remove_job(job_id)
        return {'message': 'success'}

    async def pause_by_id(self, job_id: str) -> dict:
        """Pause job_id"""
        # 暂停id对应任务，需保证job已经开启
        self.scheduler.pause_job(job_id)
        return {'message': 'success'}

    async def unpause_by_id(self, job_id: str) -> dict:
        """unpause job_id"""
        # 恢复被暂停的任务，需保证job已经开启
        self.scheduler.unpause_job(job_id)
        return {'message': 'success'}
