import json

from crawlerstack_spiderkeeper.db.models import Artifact, Project
from tests.conftest import assert_status_code, build_api_url


def test_get_multi(client, init_project, url_builder, session):
    response = client.get(url_builder('/projects'))
    assert_status_code(response)
    assert len(response.json()) == session.query(Project).count()


def test_get(client, init_project, session):
    obj = session.query(Project).first()
    api = build_api_url(f'/projects/{obj.id}')
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('id') == obj.id


def test_create(client, migrate):
    api = build_api_url('/projects')
    data = {
        'name': 'demo-1',
        'slug': 'demo_1',
    }
    response = client.post(api, data=json.dumps(data))
    assert_status_code(response)
    assert response.json().get('name') == 'demo-1'
    assert response.json().get('slug') == 'demo_1'


def test_put(client, init_project, session):
    obj = session.query(Project).first()
    api = build_api_url(f'/projects/{obj.id}')
    data = {
        'name': 'xxx'
    }
    response = client.put(api, data=json.dumps(data))
    assert_status_code(response)
    assert response.json().get('name') == 'xxx'


def test_delete(client, init_project, session):
    project = session.query(Project).first()
    count = session.query(Project).count()
    response = client.delete(build_api_url(f'/projects/{project.id}'))
    assert_status_code(response)
    assert session.query(Project).count() == count - 1


def test_delete_with_cascade(client, init_project, init_artifact, session):
    obj = session.query(Project).first()
    api = build_api_url(f'/projects/{obj.id}')
    response = client.delete(api)
    assert_status_code(response)
    count = session.query(Artifact).filter(Artifact.project_id == obj.id).count()
    assert not count


def test_delete_with_cascade_error(client, init_project, init_job, session):
    obj = session.query(Project).first()
    api = build_api_url(f'/projects/{obj.id}')
    response = client.delete(api)
    assert response.status_code == 500
