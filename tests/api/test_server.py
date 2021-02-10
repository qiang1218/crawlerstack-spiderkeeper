from crawlerstack_spiderkeeper.db.models import Server
from tests.conftest import assert_status_code, build_api_url


def test_get_multi(client, session, init_server):
    api = build_api_url('/servers')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == session.query(Server).count()


def test_get(client, session, init_server):
    obj = session.query(Server).first()
    api = build_api_url(f'/servers/{obj.id}')
    response = client.get(api)
    assert response.json().get('id') == obj.id


def test_create(client, session):
    data = {
        'name': 'test',
        'type': 'redis',
        'uri': 'redis://localhost',
    }
    api = build_api_url('/servers')
    response = client.post(api, json=data)
    assert_status_code(response)
    assert response.json().get('name') == data.get('name')


def test_update(client, session, init_server):
    obj = session.query(Server).first()
    data = {
        'name': 'test_test',
    }
    api = build_api_url(f'/servers/{obj.id}')
    response = client.put(api, json=data)
    assert_status_code(response)
    assert response.json().get('name') == data.get('name')


def test_delete(client, session, init_server):
    obj = session.query(Server).first()
    count = session.query(Server).count()
    api = build_api_url(f'/servers/{obj.id}')
    response = client.delete(api)
    assert_status_code(response)
    assert session.query(Server).count() == count - 1
