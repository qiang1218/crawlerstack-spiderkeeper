"""Task"""
from datetime import datetime
from typing import Any

from crawlerstack_spiderkeeper_scheduler.config import settings
from crawlerstack_spiderkeeper_scheduler.schemas.executor import ExecutorSchema
from crawlerstack_spiderkeeper_scheduler.schemas.task import TaskSchema
from crawlerstack_spiderkeeper_scheduler.utils import SingletonMeta
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import (
    ObjectDoesNotExist, RemoteTaskRunError)
from crawlerstack_spiderkeeper_scheduler.utils.request import \
    RequestWithSession
from crawlerstack_spiderkeeper_scheduler.utils.status import Status


class Task(metaclass=SingletonMeta):
    """task"""

    def __init__(self, task_settings):
        """init"""
        self.settings = task_settings
        self.job_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_JOB_SUFFIX
        self.artifact_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_ARTIFACT_SUFFIX
        self.server_task_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_TASK_SUFFIX
        # 使用过程基于执行器的url进行拼接
        self.executor_run_url_suffix = self.settings.EXECUTOR_RUN_SUFFIX
        # 任务中的调度器url
        self.scheduler_executor_url = self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_EXECUTOR_SUFFIX
        self.scheduler_task_url = self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_TASK_SUFFIX
        self.scheduler_task_count_url = self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_TASK_COUNT_SUFFIX
        self.max_active_task_count = self.settings.MAX_ACTIVE_TASK_COUNT

    @property
    def request_session(self):
        """request session"""
        return RequestWithSession()

    def run(self, **kwargs):
        """
        run
        :param kwargs:
        :return:
        """
        # 任务的执行逻辑： 选取执行器 -> 任务调度 -> task_record创建

        # 1. 爬虫参数
        params = self.gen_task_params(**kwargs)
        task_name = params.pop('task_name')
        job_id = kwargs.get('job_id')

        # 1.5. 获取当前job对应的任务个数，以便进行任务个数上限的控制
        active_task_count = self.get_active_task_count_by_job_id(job_id)
        if active_task_count >= self.max_active_task_count:
            return
        # 2. 获取执行器的相关信息，根据策略确定需要调度的位置，并在执行器的计数中加1
        executor = self.choose_executor(params.pop('executor_type'), params.pop('executor_selector'))

        # 3. server中task表和schedule中task表
        # 3.1 任务执行
        container_id = self.run_task(executor.url, params)
        # 3.2 创建schedule中task表
        self.create_scheduler_task_record(task_name=task_name, container_id=container_id, executor=executor,
                                          job_id=job_id)
        # 3.3 创建server中task表
        self.create_server_task_record(task_name, job_id)
        # 后续功能由外部后台任务统一管理

    def gen_task_params(self, **kwargs) -> dict[str, Any]:
        """
        Generate task params
        :param kwargs:
        :return:
        """
        # 执行任务,同时完成任务状态回溯,作为任务调用的方法存在，具体由scheduler进行触发
        # 爬虫参数
        spider_params = kwargs.get('spider_params')
        # 执行器参数
        executor_params = kwargs.get('executor_params')
        # 1. 创建对应的task，生成task_name
        job_id = kwargs.get('job_id')
        task_name = self.gen_task_name(job_id, kwargs.get('scheduler_type', 'scheduled'))
        spider_params['TASK_NAME'] = task_name

        executor_type = executor_params.pop('executor_type')
        executor_selector = executor_params.pop('executor_selector')
        return {'spider_params': spider_params,
                'executor_params': executor_params,
                'task_name': task_name,
                'executor_selector': executor_selector,
                'executor_type': executor_type}

    def get_active_executors(self, executor_type: str, status: int) -> list[ExecutorSchema]:
        """
        get active executors
        :param executor_type:
        :param status:
        :return:
        """
        # 通过接口触发获取
        resp = self.request_session.request('GET', self.scheduler_executor_url,
                                            params={'query': [f'filter_type,{executor_type}',
                                                              f'filter_status,{status}']})
        return [ExecutorSchema.parse_obj(i) for i in resp.get('data')]

    def run_task(self, url: str, params: dict) -> str:
        """
        run task
        :param url:
        :param params:
        :return:
        """
        resp = self.request_session.request('POST', url + self.executor_run_url_suffix,
                                            json=params)
        container_id = resp.get('data', {}).get('container_id')
        if container_id:
            return container_id
        raise RemoteTaskRunError()

    def create_scheduler_task_record(self, **kwargs) -> TaskSchema:
        """
        create task record
        :param kwargs:
        :return:
        """
        task_name = kwargs.pop('task_name')
        container_id = kwargs.pop('container_id')
        executor = kwargs.pop('executor')
        job_id = kwargs.pop('job_id')
        obj_in = dict(name=task_name, url=executor.url, type=executor.type, executor_id=executor.id,
                      container_id=container_id, status=Status.RUNNING.value, job_id=job_id,  # noqa
                      task_start_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        resp = self.request_session.request('POST', self.scheduler_task_url, json=obj_in)
        return TaskSchema.parse_obj(resp.get('data'))

    def get_active_task_count_by_job_id(self, job_id: str):
        """
        Get active task count with job
        :param job_id:
        :return:
        """
        # 通过接口调度，减少单任务中的依赖，filter_为数据库查询时的字段过滤前缀
        resp = self.request_session.request('GET', self.scheduler_task_count_url,
                                            params={'query': [f'filter_job_id,{job_id}',
                                                              f'filter_status,{Status.RUNNING.value}']})
        return resp.get('data', {}).get('count')

    def create_server_task_record(self, task_name: str, job_id: str) -> int:
        """
        create server task record
        :param task_name:
        :param job_id:
        :return:
        """
        # task组装
        task_create = {'name': task_name, 'job_id': job_id, 'task_status': Status.RUNNING.value}
        task = self.request_session.request('POST', self.server_task_url, json=task_create).get('data', {})
        task_id = task.get('id')
        return task_id

    def choose_executor(self, executor_type: str, selector: str) -> ExecutorSchema:
        """
        choose executor
        :param executor_type:
        :param selector:
        :return:
        """
        # todo 后续完善
        # 1. 获取活跃的执行器
        active_executors = self.get_active_executors(executor_type, Status.ONLINE.value)  # noqa
        # 2. 以选择参数为主，获取对应的executor

        # 3. 如果没有对应执行器的，则获取全部执行器任务调度个数最少的一个

        # 4. 如果有对应的执行器，则获取对应执行器中任务调度个数最少的一个
        if active_executors:
            choose_executor = active_executors[0]
            return choose_executor
        raise ObjectDoesNotExist('No active executors')

    @staticmethod
    def gen_task_name(job_id: str, scheduler_type: str = 'scheduled') -> str:
        """
        gen task name
        :param job_id:
        :param scheduler_type:
        :return:
        """
        # 生成task_name
        return job_id + '-' + scheduler_type + '-' + datetime.now().strftime('%Y%m%d%H%M%S')


def task_run(scheduler_type: str = 'scheduled', **kwargs):
    """
    task run
    :param scheduler_type: 调度类型，用于区分定时调度和手动调度
    :param kwargs:
    :return:
    """
    Task(settings).run(scheduler_type=scheduler_type, **kwargs)
