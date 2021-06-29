"""
Test artifact api.
"""
import os

import pytest

from crawlerstack_spiderkeeper.db.models import Artifact, Project
from tests.conftest import assert_status_code, build_api_url


def test_get_multi(client, session, init_artifact):
    """Test get multi artifacts"""
    api = build_api_url('/artifacts')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == session.query(Artifact).count()


def test_get(client, session, init_artifact):
    """Test get one artifact"""
    obj = session.query(Artifact).first()
    api = build_api_url(f'/artifacts/{obj.id}')
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('id') == obj.id


def test_get_project_of_artifacts(client, session, init_artifact):
    """Test get project of artifacts"""
    obj = session.query(Artifact).first()
    project_id = obj.project.id
    api = build_api_url(f'/projects/{project_id}/artifacts')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == session.query(Artifact).filter(Project.id == project_id).count()


@pytest.mark.integration
def test_create(client, session, init_project):
    """Test create artifact."""
    obj = session.query(Project).first()
    data = {
        'filename': 'xxx',
        'project_id': obj.id
    }
    api = build_api_url('/artifacts')
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('filename') == data.get('filename')


@pytest.mark.integration
def test_put(client, session, init_artifact):
    """Test update a artifact."""
    obj = session.query(Artifact).first()
    data = {
        'filename': 'xxx'
    }
    api = build_api_url(f'/artifacts/{obj.id}')
    response = client.put(api, json=data)
    assert_status_code(response)
    assert response.json().get('filename') == data.get('filename')


@pytest.mark.integration
def test_delete(client, session, init_artifact):
    """Test delete a artifact."""
    count = session.query(Artifact).count()
    obj = session.query(Artifact).first()
    api = build_api_url(f'/artifacts/{obj.id}')
    response = client.delete(api)
    assert_status_code(response)
    assert count - 1 == session.query(Artifact).count()


@pytest.mark.integration
def test_artifacts_file_upload(client, demo_zip, session, init_project):
    """Test create artifact file."""
    project = session.query(Project).first()
    data = {
        'project_id': project.id
    }
    files = {
        'file': open(demo_zip, 'rb')
    }
    response = client.post(
        build_api_url('/artifacts/files'),
        data=data,
        files=files,
    )
    assert_status_code(response)
    assert project.name in response.text


def test_artifact_files_delete(client, demo_zip):
    """Test delete a artifact file."""
    response = client.delete(
        build_api_url(f'/artifacts/files/{os.path.basename(demo_zip)}')
    )
    assert_status_code(response)
    assert not os.path.exists(demo_zip)
