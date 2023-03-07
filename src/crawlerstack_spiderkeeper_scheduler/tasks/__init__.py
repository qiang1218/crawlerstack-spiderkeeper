"""tasks"""
from crawlerstack_spiderkeeper_scheduler.signals import (server_start,
                                                         server_stop)
from crawlerstack_spiderkeeper_scheduler.tasks.executor import ExecutorTask
from crawlerstack_spiderkeeper_scheduler.tasks.task_life_cycle import LifeCycle

server_start.connect(ExecutorTask().server_start)
server_start.connect(ExecutorTask().check_executor_task)

server_stop.connect(ExecutorTask().server_stop)

# 后台任务
server_start.connect(LifeCycle().server_start)
server_start.connect(LifeCycle().check_executor_task)
server_stop.connect(LifeCycle().server_stop)
