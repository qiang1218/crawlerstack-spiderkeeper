"""
Log util.
"""
import logging
import os
from logging.config import dictConfig
from typing import Dict

from crawlerstack_spiderkeeper_executor.config import settings

DEFAULT_FORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def verbose_formatter(verbose: bool) -> str:
    """Get log fmt."""
    if verbose is True:
        return 'verbose'
    return 'simple'


def log_level(debug: bool, level: str) -> str:
    """Get log level."""
    if debug is True:
        level_num = logging.DEBUG
    else:
        level_num = logging.getLevelName(level)
    settings.set('LOGLEVEL', logging.getLevelName(level_num))
    return settings.LOGLEVEL


def init_logging_config() -> Dict:
    """
    Get log config.
    :return:
    """
    level = log_level(settings.DEBUG, settings.LOGLEVEL)

    os.makedirs(settings.LOGPATH, exist_ok=True)

    default_logging = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            'verbose': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(process)d '
                          '%(thread)d - %(pathname)s:%(lineno)d %(message)s',
            },
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s %(message)s',
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(asctime)s %(levelprefix)s '
                       '%(client_addr)s - "%(request_line)s" %(status_code)s',
            },
        },
        "handlers": {
            "console": {
                "formatter": verbose_formatter(settings.VERBOSE),
                'level': 'DEBUG',
                "class": "logging.StreamHandler",
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': verbose_formatter(settings.VERBOSE),
                'filename': os.path.join(settings.LOGPATH, 'server.log'),
                'maxBytes': 1024 * 1024 * 1024 * 200,  # 200M
                'backupCount': '5',
                'encoding': 'utf-8'
            },
            'access_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'access',
                'filename': os.path.join(settings.LOGPATH, 'access.log'),
                'maxBytes': 1024 * 1024 * 1024 * 200,  # 200M
                'backupCount': '5',
                'encoding': 'utf-8'
            },
            'register': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': verbose_formatter(settings.VERBOSE),
                'filename': os.path.join(settings.LOGPATH, 'register.log'),
                'maxBytes': 1024 * 1024 * 1024 * 200,  # 200M
                'backupCount': '5',
                'encoding': 'utf-8'
            }
        },
        "loggers": {
            '': {'level': level, 'handlers': ['console', 'file']},
            # 'uvicorn.access': {
            #     'handlers': ['access_file', 'console'],
            #     'level': level,
            #     'propagate': False
            # },
            # 'sqlalchemy.engine.base.Engine': {
            #     'handlers': ['console'],
            #     'level': level,
            #     'propagate': False
            # },
            # 'amqp.connection.Connection.heartbeat_tick': {'level': 'INFO'}
            'aiosqlite': {'level': 'INFO'},
            'crawlerstack_spiderkeeper_executor.services.register': {'level': 'INFO', 'handlers': ['register'],
                                                                     'propagate': False}},

    }
    return default_logging


def configure_logging():
    """Config log"""
    dictConfig(init_logging_config())
