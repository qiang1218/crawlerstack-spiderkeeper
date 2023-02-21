"""test file storage"""
# import tempfile
# from pathlib import Path

import pytest

from crawlerstack_spiderkeeper_server.data_storage import FileStorage

# from crawlerstack_spiderkeeper_server.utils import File


class TestFileStorage:
    """test mongo storage"""

    @pytest.fixture
    def storage(self):
        """storage fixtures"""
        return FileStorage()

    @pytest.mark.parametrize(
        'fields, datas, expect_value',
        [
            (['col1'], [['v1']], ['{"col1": "v1"}']),
            (['col1', 'col2'], [['v1', 'v2']], ['{"col1": "v1", "col2": "v2"}']),
            (['col3'], [[{'k3': 'v3'}]], ['{"col3": {"k3": "v3"}}'])
        ]
    )
    def test_concat_data(self, storage, fields, datas, expect_value):
        """test concat data"""
        result = storage.concat_data(fields, datas)
        assert result == expect_value

    def test_gen_key_name(self, storage):
        """test gen key name"""
        name = 'test'
        key_name = storage.gen_key_name(name)
        assert key_name == storage._key_prefix + 'test.json'  # pylint: disable=protected-access
    #
    # async def test_save(self, storage, temp_dir, mocker):
    #     """test create db conn"""
    #     # 测试时替换对应的连接
    #     url = 's3://access_key:secret_key@example.com:port/bucket'
    #     db, db_config = storage.transform_url(url)
    #     conn = storage.create_conn(db_config)
    #     assert conn
    #
    #     # 上传文件
    #     mocker.patch.object(FileStorage, 'bucket', new=conn.get_bucket(db))
    #     key_name = 'test.json'
    #     if storage.get(key_name):
    #         storage.get(key_name).delete()
    #
    #     key_obj = storage.get(key_name)
    #     assert key_obj is None
    #
    #     data = '{"name":"zs", "age": 30}'
    #
    #     storage.upload_string(key_name, data + '\n')
    #     key_obj = storage.get(key_name)
    #     assert key_obj
    #
    #     with tempfile.NamedTemporaryFile(
    #             mode='w',
    #             dir=temp_dir,
    #             prefix='test-write',
    #             suffix='.txt',
    #             delete=False
    #     ) as file:
    #         file.write('')
    #         file.flush()
    #         file_name = Path(file.name)
    #     key_obj.get_contents_to_filename(file_name)
    #     await File(file_name).write([data])
    #     storage.upload_file(key_name, str(file_name))
    #     # 下载对比，写入2次，三行
    #     key_obj = storage.get(key_name)
    #     content = key_obj.get_contents_as_string()
    #     assert len(content.decode().split('\n')) == 3
    #     # 删除当前的对象
    #     key_obj.delete()
