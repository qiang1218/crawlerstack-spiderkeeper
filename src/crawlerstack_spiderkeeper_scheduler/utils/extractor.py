"""extractor"""
from typing import Optional

from fastapi import Query

from crawlerstack_spiderkeeper_scheduler.config import settings


# 多内容查询时，进行请求参数的解析
def query_extractor(
        query: Optional[list[str]] = Query(None, regex='^filter_.*,.*', example='filter_name,test'),
        sort: Optional[str] = Query('id', max_length=100, example='id or id,name or -id,name'),
        limit: int = Query(settings.SIZE, le=100, alias='size'),
        offset: int = Query(settings.PAGE, alias='page')) -> dict:
    """
    Query extractor
    :param query:
    :param sort:
    :param limit:
    :param offset:
    :return:
    """
    # 针对不传参的，默认返回指定数据
    # 针对filter_name属性,需要特殊处理

    search_fields = parse_query_params(query)
    sort = sort.split(',')
    # 对q 和 sort 进行处理
    return {'search_fields': search_fields, 'sorting_fields': sort, 'limit': limit, 'offset': offset,
            'page': offset, 'size': limit}


def query_count_extractor(
        query: Optional[list[str]] = Query(None, regex='^filter_.*,.*', example='filter_name,test'),
):
    """
    Query count extractor
    :param query:
    :return:
    """
    return {'search_fields': parse_query_params(query)}


def parse_query_params(query: Optional[list[str]] = None) -> dict:
    """
    Parse query params
    :param query:
    :return:
    """
    if query:
        return {i.split(',')[0].replace('filter_', ''): i.split(',')[1] for i in query}
    return {}
