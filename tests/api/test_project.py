"""Test project api"""
import pytest
from sqlalchemy import func, select

from crawlerstack_spiderkeeper.db.models import Artifact, Project
from tests.conftest import assert_status_code, build_api_url


def test_get_multi(client, init_project):
    """Test get multi projects"""
    response = client.get(build_api_url('/projects'))
    assert_status_code(response)
    assert len(response.json()) == 2


def test_get(client, init_project):
    """Test get a project."""
    api = build_api_url('/projects/1')
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('id') == 1


def test_create(client, migrate):
    """Test create a project."""
    api = build_api_url('/projects')
    data = {
        'name': 'demo-1',
        'slug': 'demo_1',
    }
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('name') == 'demo-1'


def test_put(client, init_project):
    """Test update a project."""
    api = build_api_url(f'/projects/1')
    data = {'name': 'changed'}
    response = client.put(api, json=data)
    assert_status_code(response)
    assert response.json().get('name') == 'changed'


def test_delete(client, init_project):
    """Test delete a project."""
    response = client.delete(build_api_url(f'/projects/1'))
    assert_status_code(response)
    response = client.get(build_api_url('/projects'))
    assert int(response.headers['X-Total-Count']) == 1


def test_delete_with_cascade(client, init_project, init_artifact):
    """Test delete project with it's children."""
    api = build_api_url(f'/projects/1')
    response = client.delete(api)
    assert_status_code(response)
    response = client.get(build_api_url('/projects'))
    assert int(response.headers['X-Total-Count']) == 1


def test_delete_with_cascade_error(client, init_project, init_job):
    """Test raise exception, when delete a project with it's children."""
    api = build_api_url(f'/projects/1')
    response = client.delete(api)
    assert response.status_code == 500
