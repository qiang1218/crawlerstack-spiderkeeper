"""test mongo storage"""

import pytest

from crawlerstack_spiderkeeper_server.data_storage import MongoStorage


class TestMongoStorage:
    """test mongo storage"""

    @pytest.fixture
    def storage(self):
        """storage fixtures"""
        return MongoStorage()

    @pytest.mark.parametrize(
        'kwargs, expect_value',
        [
            ({'name': 'mongo1', 'url': 'url'}, 'mongo1'),
        ]
    )
    def test_start(self, mocker, storage, kwargs, expect_value):
        """test start"""
        # 未进行连接的创建，在结束时初始化连接关联参数
        create_conn = mocker.patch.object(MongoStorage, 'create_conn', return_value='success')
        storage_obj = storage.start(**kwargs)
        assert storage_obj.default_connector.name == expect_value
        create_conn.assert_called_once()
        storage_obj.default_connector = None
        storage_obj._connectors = {}  # pylint: disable=protected-access

    @pytest.mark.parametrize(
        'fields, datas, expect_value',
        [
            (['col1'], [['v1']], [{'col1': 'v1'}]),
            (['col1', 'col2'], [['v1', 'v2']], [{'col1': 'v1', 'col2': 'v2'}]),
            (['col3'], [[{'k3': 'v3'}]], [{'col3': {'k3': 'v3'}}])
        ]
    )
    def test_concat_data(self, storage, fields, datas, expect_value):
        """test concat data"""
        result = storage.concat_data(fields, datas)
        assert result == expect_value

    # @pytest.mark.parametrize(
    #     'url',
    #     [
    #         'mongodb://root:g0tKTzUbNEH0h541@localhost:27017/test?authSource=admin&authMechanism=DEFAULT',
    #     ]
    # )
    # def test_create_conn(self, storage, url):
    #     """test create db conn"""
    #     db, db_config = storage.transform_url(url)
    #     conn = storage.create_conn(db_config)
    #     assert conn
    #     conn[db]['foo'].drop()
    #     conn[db]['foo'].insert_many([{'name': 'foo'}])
    #     result = list(conn[db]['foo'].find())
    #     assert len(result) == 1
    #     conn[db]['foo'].drop()
    #     conn.close()
