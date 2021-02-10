import asyncio
import functools
import logging
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)


class IntervalTrigger:

    def __init__(self, interval: int):
        """
        :param interval: seconds
        """
        self.__interval = interval
        self.__start_time = datetime.now()

    @property
    def interval(self) -> int:
        return self.__interval

    def fire(self) -> None:
        self.__start_time = datetime.now()

    def next_time(self, now: Optional[datetime] = None) -> datetime:
        now = now or self.__start_time
        return now + timedelta(seconds=self.interval)


class ScheduleJob:

    def __init__(
            self,
            func: Callable,
            interval: int,
            id_: int,
            name: str,
            args: Optional[Union[List, Set]] = None,
            kwargs: Optional[Dict] = None
    ):
        self.__func = func

        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        self.__wrapper_func = functools.partial(func, *args, **kwargs)  # 包装一层，减少在内部传递参数

        self.__id = id_
        self.__name = name or str(func)

        self.__trigger = IntervalTrigger(interval)

        self.__running = False
        self.__count = 0
        self.__loop = asyncio.get_running_loop()

    def __repr__(self) -> str:
        return self.__name

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def trigger(self) -> IntervalTrigger:
        return self.__trigger

    @property
    def is_running(self) -> bool:
        return self.__running

    async def run(self) -> None:
        """
        如果正在执行任务，则跳过本次运行，会在下次时间再次触发
        :return:
        """
        self.trigger.fire()
        if self.__running:
            logger.info(f'Job {self.name} is running, skip trigger. Next run time {self.trigger.next_time()}')
        else:
            logger.info(
                f'Start run job {self.name}, this is {self.__count} times. Next run time {self.trigger.next_time()}'
            )
            self.__running = True
            if asyncio.iscoroutinefunction(self.__func):
                await self.__loop.create_task(self.__wrapper_func())
            else:
                await self.__loop.run_in_executor(None, self.__wrapper_func())
            self.__running = False
            self.__count += 1


class Scheduler:
    __obj = None

    def __new__(cls, *args, **kwargs):
        if cls.__obj is None:
            cls.__obj = super().__new__(cls)
        return cls.__obj

    def __init__(self, max_interval: int = 5, loop: Optional[AbstractEventLoop] = None):
        self.__max_interval = max_interval
        self.__jobs: List[ScheduleJob] = []
        self.__running_jobs: List[asyncio.Task] = []
        self.__stop = False

        self.__loop = loop or asyncio.get_event_loop()

        self.__process_job_task: Optional[asyncio.Task] = None

    def submit(
            self,
            func: Callable,
            interval: int,
            id_: int,
            name: str,
            args=None,
            kwargs=None) -> ScheduleJob:
        """
        提交任务到调度器
        :param func:
        :param interval:
        :param id_
        :param args:
        :param name:
        :param kwargs:
        :return:
        """
        job = ScheduleJob(func, interval, id_, name, args, kwargs)
        self.__jobs.append(job)
        logger.info(f'Submit task {job} to scheduler')
        return job

    def remove(self, job: ScheduleJob) -> None:
        """
        从调度器删除任务
        :param job:
        :return:
        """
        logger.info(f'Remove task {job}')
        self.__jobs.remove(job)

    def _task_finish(self, task: asyncio.Task) -> None:
        self.__running_jobs.remove(task)

    def _run_job(self, job: ScheduleJob):
        fut = self.__loop.create_task(job.run())
        self.__running_jobs.append(fut)
        fut.add_done_callback(self.__running_jobs.remove)

    async def _process_job(self):
        """
        处理任务
        :return:
        """
        logger.info(f'Scheduler start process job......')
        while True:
            if self.__stop:
                break

            now = datetime.now()
            next_wake_time = now + timedelta(seconds=self.__max_interval)
            min_interval = self.__max_interval
            jobs = self.__jobs
            for job in jobs:
                if job.trigger.interval < 0:
                    # 对于时间间隔小于 0 的任务只执行一次，然后将任务删除
                    self._run_job(job)
                    self.remove(job)
                    continue

                if job.trigger.next_time() < now:
                    self._run_job(job)
                min_interval = min(min_interval, job.trigger.interval)
                next_wake_time = min(next_wake_time, job.trigger.next_time())

            delta = next_wake_time - now

            sleep = min_interval
            if delta.days >= 0:
                sleep = round(delta.days * 3600 + delta.seconds + delta.microseconds / 10e6, 2)

            if sleep > 0.5:
                logger.info(f'Scheduler delay {sleep} seconds....')
                await asyncio.sleep(sleep)
            elif sleep < 0:
                await asyncio.sleep(min_interval)
                logger.warning(f'Process job delay {sleep}')
            else:
                continue
            print('')

        logger.info(f'Schedule process job stopping......')
        for task in self.__running_jobs:
            cancelled = task.cancel()
            if cancelled:
                logger.info(f'Cancel task {task}.')

    async def start(self) -> None:
        """启动调度器"""
        logger.info(f'Start scheduler.')
        self.__process_job_task = self.__loop.create_task(self._process_job())

    async def stop(self) -> None:
        """停止调度器"""
        self.__stop = True
        logger.info(f'Scheduler stopping...')
        if self.__process_job_task:
            await self.__process_job_task
        logger.info(f'Scheduler is stop.')


scheduler = Scheduler()
