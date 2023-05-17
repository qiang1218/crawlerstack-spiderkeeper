"""Test pulsar"""
import pytest

from crawlerstack_spiderkeeper_server.data_storage.pulsar import PulsarStorage

# from pulsar.schema import schema


class TestPulsarStorage:
    """Test pulsar storage"""

    @pytest.fixture
    def storage(self):
        return PulsarStorage()

    # @pytest.mark.parametrize(
    #     'url',
    #     ['pulsar://localhost:6650?token=aaa&topic_prefix=bbb']
    # )
    # def test_create_conn(self, storage, url):
    #     """Test create conn"""
    #     db, db_config = storage.transform_url(url)
    #     conn = storage.create_conn(db_config)
    #     assert conn

    # @pytest.mark.parametrize(
    #     'name, url, data, topic, expect_value',
    #     [
    #         ('test',
    #          'pulsar://localhost:6650?token=aaa.bbb.ccc&topic_prefix=public/spiderkeeper',
    #          {'title': 'foo', 'fields': ['name'], 'datas': [['bar']]},
    #          'persistent://public/spiderkeeper/foo',
    #          '{"name": "bar"}'
    #          )
    #     ]
    # )
    # async def test_save(self, storage, name, url, data, topic, expect_value):
    #     """Test save"""
    #     storage.start(name=name, url=url)
    #     await storage.save(data)
    #
    #     # 消费
    #     consumer = storage.default_connector.conn.subscribe(topic, 'test', schema=schema.StringSchema(),
    #                                                         start_message_id_inclusive=False)
    #
    #     for i in range(1):
    #         msg = consumer.receive()
    #         consumer.acknowledge(msg)
    #         assert msg.value() == expect_value
