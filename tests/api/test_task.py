"""
Test task api
"""

from crawlerstack_spiderkeeper.db.models import Task
from tests.conftest import assert_status_code, build_api_url


def test_get_multi(client, session, init_task):
    """Test get multi task."""
    api = build_api_url('/tasks')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == session.query(Task).count()


def test_get(client, session, init_task):
    """Test get a task."""
    obj = session.query(Task).first()
    api = build_api_url(f'/tasks/{obj.id}')
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('id') == obj.id


def test_delete(client, session, init_task):
    """Test delete a task."""
    obj = session.query(Task).first()
    count = session.query(Task).count()
    api = build_api_url(f'/tasks/{obj.id}')
    response = client.delete(api)
    assert_status_code(response)
    assert session.query(Task).count() == count - 1
