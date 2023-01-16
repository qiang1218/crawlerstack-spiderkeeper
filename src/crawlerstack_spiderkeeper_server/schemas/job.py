"""
Job schema
"""
from pydantic import (BaseModel, constr,  # pylint: disable=no-name-in-module
                      validator)

from crawlerstack_spiderkeeper_server.schemas.base import InDBMixin
from crawlerstack_spiderkeeper_server.utils import transform_cron_expression


class JobBase(BaseModel):
    """Job base schema."""
    name: constr(max_length=200) = None
    cmdline: constr(max_length=500) = None
    environment: constr(max_length=2000) = None
    volume: constr(max_length=2000) = None
    trigger_expression: constr(max_length=100) = None
    storage_enable: bool = False
    storage_server_id: int = None
    executor_type: constr(max_length=100) = None
    enabled: bool = False
    pause: bool = False
    executor_selector: constr(max_length=100) = None
    artifact_id: int = None

    @validator('trigger_expression')
    def check_url(cls, value: str):  # pylint: disable=no-self-argument
        """check trigger_expression"""
        if isinstance(value, str):
            # 考虑apscheduler接收5位，现仅判断个数，后续扩充
            trans_value = transform_cron_expression(value)
            values = trans_value.split()
            if len(values) != 5:
                raise ValueError('Wrong number of fields; got {}, expected 5'.format(len(values)))
            return trans_value
        raise ValueError('url must be URL object or URL string')


class JobSchema(JobBase, InDBMixin):
    """Job model schema."""


class JobCreate(JobBase):
    """Job create schema."""
    name: constr(max_length=200)
    trigger_expression: constr(max_length=100)
    storage_enable: bool
    executor_type: constr(max_length=100)
    artifact_id: int


class JobUpdate(JobBase):
    """Job update schema."""
