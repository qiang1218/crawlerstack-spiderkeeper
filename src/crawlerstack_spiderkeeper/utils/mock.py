"""Async mock"""
from unittest.mock import MagicMock


class AsyncMock(MagicMock):
    """
    AsyncMock
    ref: https://stackoverflow.com/a/32498408/11722440

    Usage:

    ```
    mocker.patch.object(foo, 'bar', new_callable=AsyncMock)
    ```
    """

    async def __call__(self, *args, **kwargs):  # pylint: disable=invalid-overridden-method, useless-super-delegation
        return super().__call__(*args, **kwargs)

    def __await__(self):
        return self
