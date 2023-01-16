"""test utils"""
import pytest

from crawlerstack_spiderkeeper_server.data_storage.utils import \
    transform_mysql_db_str

key_list = ['user', 'password', 'host', 'port', 'database', 'charset']


@pytest.mark.parametrize(
    'db_str, expect_value',
    [
        ('mysql://root:root@localhost:3306/spiderkeeper_server?charset=utf8',
         {'user': 'root', 'password': 'root', 'host': 'localhost', 'port': '3306', 'database': 'spiderkeeper_server',
          'charset': 'utf8'}),
    ]
)
def test_transform_mysql_db_str(db_str, expect_value):
    """test transform mysql db str"""
    result = transform_mysql_db_str(db_str)
    assert result
    for key in key_list:
        assert result.get(key) == expect_value.get(key)
