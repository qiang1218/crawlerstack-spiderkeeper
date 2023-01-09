"""test log config."""
import pytest

from crawlerstack_spiderkeeper_server.utils.log import log_level, verbose_formatter


@pytest.mark.parametrize(
    ['verbose', 'except_value'],
    [
        (True, 'verbose'),
        (False, 'simple'),
    ]
)
def test_verbose_formatter(verbose, except_value):
    """Test verbose format."""
    res = verbose_formatter(verbose)
    assert res == except_value


@pytest.mark.parametrize(
    ['debug', 'level', 'except_value'],
    [
        (True, 'DEBUG', 'DEBUG'),
        (True, 'INFO', 'DEBUG'),
        (True, 'ERROR', 'DEBUG'),
        (False, 'DEBUG', 'DEBUG'),
        (False, 'INFO', 'INFO'),
    ]
)
def test_log_level(debug, level, except_value):
    """Test log level."""
    res = log_level(debug, level)
    assert res == except_value
