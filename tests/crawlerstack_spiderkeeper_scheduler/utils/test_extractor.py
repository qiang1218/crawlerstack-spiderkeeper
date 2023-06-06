"""Test extractor"""
import pytest

from crawlerstack_spiderkeeper_scheduler.utils.extractor import (
    parse_query_params, query_count_extractor, query_extractor)


@pytest.mark.parametrize(
    'input_value, expect_output',
    [
        (['filter_name,foo'], {'search_fields': {'name': 'foo'}}),
        (['filter_name,foo', 'filter_age,12'], {'search_fields': {'name': 'foo', 'age': '12'}}),
        (['name,foo'], {'search_fields': {'name': 'foo'}})
    ]
)
def test_query_count_extractor(input_value, expect_output):
    """Test query count extractor"""
    # Query参数在get的请求参数拆分时生效，不符合规则的422退出
    assert query_count_extractor(input_value) == expect_output


@pytest.mark.parametrize(
    'input_value, expect_output',
    [
        (['filter_name,foo', 'filter_age,12'], {'name': 'foo', 'age': '12'}),
        (['filter_name,foo'], {'name': 'foo'}),
        (['name,foo'], {'name': 'foo'}),
        (None, {})
    ]
)
def test_parse_query_params(input_value, expect_output):
    """Test parse_query_params"""
    assert parse_query_params(input_value) == expect_output


@pytest.mark.parametrize(
    'query, sort, limit, offset, expect_output',
    [
        (['filter_name,foo'], 'id', 1, 0,
         {'search_fields': {'name': 'foo'}, 'sorting_fields': ['id'], 'limit': 1, 'offset': 0, 'page': 0, 'size': 1})
    ]
)
def test_query_extractor(query, sort, limit, offset, expect_output):
    """Test query extract"""
    assert query_extractor(query, sort, limit, offset) == expect_output
