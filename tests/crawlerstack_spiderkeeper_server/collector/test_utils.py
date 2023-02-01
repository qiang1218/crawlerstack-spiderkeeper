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
        # await asyncio.sleep(0)
        data = json.loads(data)
        assert data['msg'] == 'foo'

    def consume_and_auto_ack(loop: AbstractEventLoop, body, message):
        """Registered the callback to consumer """
        # To submit a coroutine object to the event loop. (thread safe)
        fut = asyncio.run_coroutine_threadsafe(use_data(body), loop)
        fut.result(5)  # Wait for the result from other os thread
        message.ack()  # then manual ack

    callback = functools.partial(consume_and_auto_ack, asyncio.get_running_loop())
    await kombu.consume(
        queue_name='foo',
        routing_key='bar',
        exchange_name='foo',
        register_callbacks=[callback],
    )

    await kombu.server_stop()
