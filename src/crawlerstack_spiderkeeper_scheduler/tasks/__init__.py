"""tasks"""
from crawlerstack_spiderkeeper_scheduler.signals import (server_start,
                                                         server_stop)
from crawlerstack_spiderkeeper_scheduler.tasks.executor import ExecutorTask

server_start.connect(ExecutorTask().server_start)
server_start.connect(ExecutorTask().check_executor_task)

server_stop.connect(ExecutorTask().server_stop)
