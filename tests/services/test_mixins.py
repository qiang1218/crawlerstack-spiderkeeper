import pytest

from crawlerstack_spiderkeeper.services.mixinx import Demo


@pytest.mark.asyncio
async def test_mixins():
    demo = Demo()
    async for x in demo.consuming(5):
        print(x)
