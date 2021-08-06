"""
Log service.
"""
import functools
import logging
from typing import Any, Dict, List

from kombu import Message

from crawlerstack_spiderkeeper.services.base import Kombu

logger = logging.getLogger(__name__)


class LogService(Kombu):
    """
    日志服务接受爬虫程序自身产生的日志，将日志写入队列。同时对外提供搞获取日志的接口
    """
    exchange_name = 'log'


