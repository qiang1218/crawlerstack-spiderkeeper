"""
Test task api
"""
import pytest
from sqlalchemy import select, func

from crawlerstack_spiderkeeper.db.models import Task
from tests.conftest import assert_status_code, build_api_url


def test_get_multi(client, init_task):
    """Test get multi task."""
    api = build_api_url('/tasks')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == 2


def test_get(client, init_task):
    """Test get a task."""
    api = build_api_url(f'/tasks/1')
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('id') == 1


@pytest.mark.asyncio
async def test_delete(client, init_task, session):
    """Test delete a task."""
    api = build_api_url(f'/tasks/1')
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(Task))
    assert result == 1
