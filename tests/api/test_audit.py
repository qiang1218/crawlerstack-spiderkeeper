from crawlerstack_spiderkeeper.db.models import Audit
from tests.conftest import assert_status_code, build_api_url


def test_get_multi(client, session, init_audit):
    api = build_api_url(f'/audits')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == session.query(Audit).count()


def test_get(client, session, init_audit):
    obj = session.query(Audit).first()
    api = build_api_url(f'/audits/{obj.id}')
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('id') == obj.id
