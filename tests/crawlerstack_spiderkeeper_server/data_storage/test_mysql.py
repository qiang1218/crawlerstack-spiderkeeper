"""test mysql storage"""
from datetime import datetime, timedelta

import pytest

from crawlerstack_spiderkeeper_server.data_storage import MysqlStorage
from crawlerstack_spiderkeeper_server.data_storage.base import Connector


class TestMysqlStorage:

    @pytest.fixture
    def storage(self):
        """storage fixtures"""
        return MysqlStorage()

    @pytest.mark.parametrize(
        'kwargs, expect_value',
        [
            ({'name': 'mysql1', 'url': 'url'}, 'mysql1'),
        ]
    )
    def test_start(self, mocker, storage, kwargs, expect_value):
        """test start"""
        # 未进行连接的创建，在结束时初始化连接关联参数
        create_db_conn = mocker.patch.object(MysqlStorage, 'create_db_conn', return_value='')
        storage_obj = storage.start(**kwargs)
        assert storage_obj.default_connector.name == expect_value
        create_db_conn.assert_called_once()
        storage_obj.default_connector = None
        storage_obj._connectors = {}

    @pytest.mark.parametrize(
        'url, name, data, insert_sql, table_sql, drop_sql, select_sql, expect_value',
        [
            ('mysql://root:1qazZAQ!@localhost:3306/spiderkeeper_server?charset=utf8', 'mysql1',
             {'datas': ['row1', 'row2']}, 'INSERT IGNORE INTO test1(column1) VALUES (%s)',
             'create table if not exists test1(column1 varchar(100) not null)',
             'drop table test1', 'select count(*) from test1', 2),
        ]
    )
    def test_save(self, mocker, storage, url, name, data, insert_sql, table_sql, drop_sql, select_sql, expect_value):
        """test save"""
        sql = mocker.patch.object(MysqlStorage, 'sql', return_value=insert_sql)
        # 初始化连接
        storage.default_connector = Connector(
            name=name, url=url,
            conn=storage.create_db_conn(url),
            expire_date=datetime.now() + timedelta(storage.expire_day)
        )
        # 创建表
        cursor = storage.default_connector.conn.cursor()
        cursor.execute(table_sql)
        storage.default_connector.conn.commit()
        # 核心逻辑
        status = storage.save(data)
        assert status
        # 判断
        cursor.execute(select_sql)
        result = cursor.fetchone()
        assert result[0] == expect_value
        # 删除表
        cursor.execute(drop_sql)
        storage.default_connector.conn.commit()
        cursor.close()
        sql.assert_called_once()

    @pytest.mark.parametrize(
        'table_name, fields, expect_value',
        [
            ('test1', ['column1', 'column2'], 'INSERT IGNORE INTO test1(column1,column2) VALUES (%s,%s)'),
            ('test1', ['column1'], 'INSERT IGNORE INTO test1(column1) VALUES (%s)'),
        ]
    )
    def test_sql(self, storage, table_name, fields, expect_value):
        """test sql"""
        result = storage.sql(table_name, fields)
        assert result == expect_value

    # 考虑本地测试，提交时需注释
    @pytest.mark.parametrize(
        'url, expect_value',
        [
            ('mysql://root:1qazZAQ!@localhost:3306/spiderkeeper_server?charset=utf8', 5),
        ]
    )
    def test_create_db_conn(self, storage, url, expect_value):
        """test create db conn"""
        conn = storage.create_db_conn(url)
        assert conn
        cursor = conn.cursor()
        cursor.execute(f'select {expect_value}')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        assert result[0] == expect_value