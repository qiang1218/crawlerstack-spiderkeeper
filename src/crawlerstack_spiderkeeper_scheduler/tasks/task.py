"""task"""
import json
import time
from datetime import datetime
from typing import Any

from crawlerstack_spiderkeeper_scheduler.config import settings
from crawlerstack_spiderkeeper_scheduler.schemas.executor import ExecutorSchema
from crawlerstack_spiderkeeper_scheduler.schemas.task import (TaskCreate,
                                                              TaskSchema,
                                                              TaskUpdate)
from crawlerstack_spiderkeeper_scheduler.utils import SingletonMeta
from crawlerstack_spiderkeeper_scheduler.utils.exceptions import \
    RemoteTaskRunError
from crawlerstack_spiderkeeper_scheduler.utils.request import \
    RequestWithSession
from crawlerstack_spiderkeeper_scheduler.utils.status import (ExceptStatus,
                                                              Status)


class Task(metaclass=SingletonMeta):
    """task"""

    def __init__(self, task_settings):
        """init"""
        self.settings = task_settings
        self.job_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_JOB_SUFFIX
        self.artifact_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_ARTIFACT_SUFFIX
        self.server_task_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_TASK_SUFFIX
        self.server_task_crud_url = self.settings.SERVER_BASE_URL + self.settings.SERVER_TASK_CRUD_SUFFIX
        # 使用过程基于执行器的url进行拼接
        self.executor_run_url_suffix = self.settings.EXECUTOR_RUN_SUFFIX
        self.executor_wait_url_suffix = self.settings.EXECUTOR_WAIT_SUFFIX
        self.executor_rm_url_suffix = self.settings.EXECUTOR_RM_SUFFIX
        # 任务中的调度器url
        self.scheduler_executor_url = self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_EXECUTOR_SUFFIX
        self.scheduler_executor_crud_url = \
            self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_EXECUTOR_CRUD_SUFFIX
        self.scheduler_task_url = self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_TASK_SUFFIX
        self.scheduler_task_crud_url = self.settings.SCHEDULER_BASE_URL + self.settings.SCHEDULER_TASK_CRUD_SUFFIX

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
        # 执行任务,同时完成任务状态回溯,作为任务调用的方法存在，具体由scheduler进行触发，同时数据获取和更新采用
        # 接口触发的方式进行

        # 1. 爬虫参数
        params = self.gen_task_params(**kwargs)
        task_name = params.pop('task_name')

        # 2. 获取执行器的相关信息，根据策略确定需要调度的位置，并在执行器的计数中加1
        executor = self.choose_executor(params.pop('executor_type'), params.pop('executor_selector'))

        # 3. server中task表和schedule中task表
        # 3.1 任务执行
        container_id = self.run_task(executor.url, params)
        # 3.2 执行器计数+1
        self.update_task_count(executor.id, symbol=True)

        # 3.2 创建schedule中task表
        task = self.create_scheduler_task_record(task_name=task_name, container_id=container_id, executor=executor)

        # 3.3 创建server中task表
        server_task_id = self.create_server_task_record(task_name)

        # 4. 任务状态检测
        # 任务状态的更新机制，根据容器的状态进行更新，默认created状态
        _status = Status.CREATED.name
        while True:
            # 确保创建后的容器会退出，考虑时间延后问题，如果容器已经退出，则状态的完整性更新
            status = self.get_task_status(executor.url, container_id)
            if status != _status:
                _status = status
                # 任务状态更新操作
                self.update_server_task_record(pk=server_task_id, status=Status[status].value)  # noqa
                # scheduler中task表状态更新
                self.update_scheduler_task_record(pk=task.id, status=Status[status].value, task_end_time=datetime.now())
                # 如果退出状态时，循环终止
                if _status in ExceptStatus.list():
                    break
            time.sleep(5)
        # 5.3 调度器中detail表任务个数状态更新
        self.update_task_count(executor.id, symbol=False)
        # 5.4 执行器的任务对应container_id任务清除
        self.remove_container(executor.url, container_id=container_id)

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
        task_name = self.gen_task_name(job_id)
        spider_params['TASK_NAME'] = task_name

        executor_type = executor_params.pop('executor_type')
        executor_selector = executor_params.pop('executor_selector')
        return {'spider_params': spider_params,
                'executor_params': executor_params,
                'task_name': task_name,
                'executor_selector': executor_selector,
                'executor_type': executor_type}

    def remove_container(self, url: str, container_id: str):
        """remove container from remote executor"""
        self.request_session.request('GET', url + self.executor_rm_url_suffix % container_id)

    def get_active_executors(self, executor_type: str, status: int) -> list[ExecutorSchema]:
        """
        get active executors
        :param executor_type:
        :param status:
        :return:
        """
        # 通过接口触发获取
        resp = self.request_session.request('GET', self.scheduler_executor_url,
                                            params={'filter_type': executor_type,
                                                    'filter_status': status})
        return resp.get('data')

    def run_task(self, url: str, params: dict):
        """
        run task
        :param url:
        :param params:
        :return:
        """
        resp = self.request_session.request('POST', url + self.executor_run_url_suffix,
                                            json=json.dumps(params))
        container_id = resp.get('data', {}).get('container_id')
        if container_id:
            return container_id
        raise RemoteTaskRunError()

    def get_task_status(self, url: str, container_id: str) -> str:
        """
        get task status
        :param url:
        :param container_id:
        :return:
        """
        resp = self.request_session.request('GET', url + self.executor_wait_url_suffix % container_id)
        return resp.get('data', {}).get('status')

    def create_scheduler_task_record(self, **kwargs) -> TaskSchema:
        """
        create task record
        :param kwargs:
        :return:
        """
        task_name = kwargs.pop('task_name')
        container_id = kwargs.pop('container_id')
        executor = kwargs.pop('executor')
        obj_in = TaskCreate(name=task_name, url=executor.url, type=executor.type, executor_id=executor.id,
                            container_id=container_id, status=Status.CREATED.value)  # noqa
        resp = self.request_session.request('POST', self.scheduler_task_url, json=obj_in)
        return resp.get('data')

    def update_scheduler_task_record(self, pk: int, **kwargs) -> TaskSchema:
        """
        update task record
        :param pk:
        :param kwargs:
        :return:
        """
        # 主要字段为 status 和 task_end_time
        obj_in = TaskUpdate(status=kwargs.pop('status'), task_end_time=kwargs.pop('task_end_time'))
        resp = self.request_session.request('PATCH', self.scheduler_task_crud_url % pk, json=obj_in)
        return resp.get('data')

    def create_server_task_record(self, task_name: str) -> int:
        """
        create server task record
        :param task_name:
        :return:
        """
        # task组装
        task_create = {'name': task_name}
        task = self.request_session.request('POST', self.server_task_url, json=task_create).get('data', {})
        task_id = task.get('id')
        return task_id

    def update_server_task_record(self, pk: int, status: int) -> dict:
        """
        update server task record
        :param pk:
        :param status:
        :return:
        """
        task = {'status': status}
        return self.request_session.request('PATCH', self.server_task_crud_url % pk, json=task)

    def update_task_count(self, pk: int, symbol: bool):
        """
        update executor task count
        :param pk:
        :param symbol:
        :return:
        """
        executor = self.get_executor_by_pk(pk)
        if symbol:
            task_count = executor.task_count + 1
        else:
            task_count = executor.task_count - 1

        return self.request_session.request('PATCH', self.scheduler_executor_crud_url % pk,
                                            json={'task_count': task_count})

    def get_executor_by_pk(self, pk: int) -> ExecutorSchema:
        """
        get executor task count
        :param pk:
        :return:
        """
        resp = self.request_session.request('GET', self.scheduler_executor_crud_url % pk)
        return resp.get('data')

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
        return active_executors[0]

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


def task_run(**kwargs):
    """
    task run
    :param kwargs:
    :return:
    """
    Task(settings).run(**kwargs)
