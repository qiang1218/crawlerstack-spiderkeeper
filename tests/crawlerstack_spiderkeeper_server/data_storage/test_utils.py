"""Test utils"""
import pytest

from crawlerstack_spiderkeeper_server.data_storage.utils import (
    transform_mongo_db_str, transform_mysql_db_str, transform_pulsar_url,
    transform_s3_url)

key_list = ['user', 'password', 'host', 'port', 'database', 'charset']


@pytest.mark.parametrize(
    'url, expect_value',
    [
        ('mysql://root:root@localhost:3306/spiderkeeper_server?charset=utf8',
         {'user': 'root', 'password': 'root', 'host': 'localhost', 'port': '3306', 'database': 'spiderkeeper_server',
          'charset': 'utf8'}),
    ]
)
def test_transform_mysql_db_str(url, expect_value):
    """Test transform mysql db str"""
    result = transform_mysql_db_str(url)
    assert result
    for key in key_list:
        assert result.get(key) == expect_value.get(key)


@pytest.mark.parametrize(
    'url, expect_value',
    [
        ('mongodb://user:password@example.com/default_db?authSource=admin',
         {'url': 'mongodb://user:password@example.com/default_db?authSource=admin', 'database': 'default_db'})
    ]
)
def test_transform_mongo_db_str(url, expect_value):
    """Test transform mongo db str"""
    result = transform_mongo_db_str(url)
    assert result == expect_value


@pytest.mark.parametrize(
    'url, expect_value',
    [
        ('s3://user:password@example.com:port/bucket',
         {'type': 's3', 'access_key': 'user', 'secret_key': 'password', 'host': 'example.com:port', 'bucket': 'bucket'})
    ]
)
def test_transform_s3_url(url, expect_value):
    """Test transform s3 url"""
    result = transform_s3_url(url)
    assert result == expect_value


@pytest.mark.parametrize(
    'url, expect_value',
    [
        ('pulsar://localhost:6650?token=aaa.bbb.ccc&topic_prefix=clusterId/namespace',
         {'url': 'pulsar://localhost:6650', 'token': 'aaa.bbb.ccc', 'topic_prefix': 'clusterId/namespace'})
    ]
)
def test_transform_pulsar_url(url, expect_value):
    """Test transform pulsar url"""
    result = transform_pulsar_url(url)
    assert result == expect_value
