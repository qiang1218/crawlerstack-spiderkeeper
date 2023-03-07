"""test utils"""
import asyncio
import functools
import json
from asyncio import AbstractEventLoop
from datetime import datetime

from crawlerstack_spiderkeeper_server.collector import Kombu


class DemoKombu(Kombu):
    """Demo Kombu mixin."""
    NAME = 'test'


async def test_kombu():
    """
    test kombu
    :return:
    """
    kombu = DemoKombu()
    await kombu.server_start()

    await kombu.publish(
        queue_name='foo',
        routing_key='bar',
        exchange_name='foo',
        body=json.dumps({
            'datetime': datetime.now().strftime('%Y-%h-%mT%H:%M:%S+0800'),
            'msg': 'foo'
        })
    )

    await asyncio.sleep(0)

    async def use_data(data):
        """consume then have to do some coroutine"""
        data = json.loads(data)
        assert data['msg'] == 'foo'

    def consume_and_auto_ack(loop: AbstractEventLoop, body, message):
        """Registered the callback to consumer """
        fut = asyncio.run_coroutine_threadsafe(use_data(body), loop)
        fut.result(5)
        message.ack()

    callback = functools.partial(consume_and_auto_ack, asyncio.get_running_loop())
    await kombu.consume(
        queue_name='foo',
        routing_key='bar',
        exchange_name='foo',
        register_callbacks=[callback],
    )
    await asyncio.sleep(0.001)
    await kombu.start_consume(limit=1, loop=asyncio.get_running_loop())
    await asyncio.sleep(0.001)

    await asyncio.sleep(2)
