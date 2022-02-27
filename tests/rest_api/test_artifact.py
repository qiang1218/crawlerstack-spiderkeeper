"""
Test artifact api.
"""
import os

import pytest

from crawlerstack_spiderkeeper.db.models import Artifact, Project
from tests.conftest import assert_status_code, build_api_url


def test_get(client, init_artifact):
    """Test get multi artifacts"""
    api = build_api_url('/artifacts')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == 2
    assert int(response.headers['X-Total-Count']) == 2


def test_get_by_id(client, init_artifact):
    """Test get one artifact"""
    api = build_api_url(f'/artifacts/1')
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('id') == 1


@pytest.mark.integration
def test_create(client, init_project, demo_zip):
    """Test create artifact."""
    data = {
        'project_id': 1,
        'execute_path': '',
        'interpreter': '',
    }
    with open(demo_zip, 'rb') as file:
        api = build_api_url('/artifacts')
        response = client.post(
            api,
            data=data,
            files={
                'file': file
            }
        )
        assert_status_code(response)
        assert response.json().get('filename')


@pytest.mark.integration
def test_put(client, init_artifact):
    """Test update a artifact."""
    data = {
        'filename': 'xxx'
    }
    api = build_api_url(f'/artifacts/1')
    response = client.put(api, json=data)
    assert_status_code(response)
    assert response.json().get('filename') == data.get('filename')


@pytest.mark.integration
def test_delete(client, init_artifact):
    """Test delete a artifact."""
    api = build_api_url(f'/artifacts/1')
    response = client.delete(api)
    assert_status_code(response)
    response = client.get(build_api_url('/artifacts'))
    assert int(response.headers['X-Total-Count']) == 1


@pytest.mark.integration
def test_artifacts_file_upload(client, demo_zip, init_project):
    """Test create artifact file."""
    project = init_project[0]
    data = {
        'project_id': project.id
    }
    with open(demo_zip, 'rb') as file:
        files = {
            'file': file
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
