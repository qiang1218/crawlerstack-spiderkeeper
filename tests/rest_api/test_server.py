"""
Test server api.
"""
import pytest
from sqlalchemy import func, select

from crawlerstack_spiderkeeper.db.models import Server
from tests.conftest import assert_status_code, build_api_url


def test_get_multi(client, init_server):
    """Test get multi server"""
    api = build_api_url('/servers')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == 2


def test_get(client, init_server):
    """Test get a server."""
    api = build_api_url(f'/servers/1')
    response = client.get(api)
    assert response.json().get('id') == 1


def test_create(client):
    """TEst create a server."""
    data = {
        'name': 'test',
        'type': 'redis',
        'uri': 'redis://localhost',
    }
    api = build_api_url('/servers')
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('name') == data.get('name')


def test_update(client, init_server):
    """Test update a server."""
    data = {
        'name': 'test_test',
    }
    api = build_api_url(f'/servers/1')
    response = client.put(api, json=data)
    assert_status_code(response)
    assert response.json().get('name') == data.get('name')


@pytest.mark.asyncio
async def test_delete(client, init_server, session):
    """Test delete a server."""
    api = build_api_url(f'/servers/1')
    response = client.delete(api)
    assert_status_code(response)

    result = await session.scalar(select(func.count()).select_from(Server))
    assert result == 1
