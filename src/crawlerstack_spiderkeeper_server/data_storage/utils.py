"""utils"""
import dataclasses
import re
from datetime import datetime
from typing import Any

MYSQL_PATTERN = re.compile(
    r'^.*:\/\/(?P<user>.*):(?P<password>.*)@(?P<host>.*):(?P<port>.*)\/(?P<database>.*)\?(charset=)+(?P<charset>.*)$')
MONGO_PATTERN = re.compile(r'.*\/(?P<database>.*)\?.*')
S3_PATTERN = re.compile(r'^(?P<type>.*):\/\/(?P<access_key>.*):(?P<secret_key>.*)@(?P<host>.*)\/(?P<bucket>.*)')


def transform_mysql_db_str(url: str) -> dict:
    """Transform a database string"""
    # mysql://root:root@localhost:3306/spiderkeeper_server?charset=utf8
    matcher = MYSQL_PATTERN.match(url)
    if matcher:
        return matcher.groupdict()
    return {}


def transform_mongo_db_str(url: str) -> dict:
    """Transform a MongoDB database string"""
    # 设置mongo的链接串,暂时默认为通用的格式
    # mongodb://user:password@example.com/default_db?authSource=admin
    data = {'url': url}
    matcher = MONGO_PATTERN.match(url)
    if matcher:
        data.update(matcher.groupdict())
    return data


def transform_s3_url(url: str) -> dict:
    """Transform a s3 url"""
    # 定义s3的连接规则
    # s3://access_key:secret_key@example.com:port/bucket
    matcher = S3_PATTERN.match(url)
    if matcher:
        return matcher.groupdict()
    return {}


@dataclasses.dataclass
class Connector:
    """Connector"""
    # 通用配置
    name: str
    url: str
    expire_date: datetime
    conn: Any
    db: str
