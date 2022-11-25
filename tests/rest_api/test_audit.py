"""
Test audit api.
"""

from tests.conftest import assert_status_code, build_api_url


def test_get_multi(client, init_audit):
    """Test get multi audits."""
    api = build_api_url('/audits')
    response = client.get(api)
    assert_status_code(response)
    assert len(response.json()) == 2


def test_get(client, session, init_audit):
    """Test get one audit."""
    api = build_api_url(f'/audits/1')
    response = client.get(api)
    assert_status_code(response)
    assert response.json().get('id') == 1
