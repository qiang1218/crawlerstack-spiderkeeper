"""test reqeust"""
import json

import pytest
from requests import Response, Session

from crawlerstack_spiderkeeper_server.utils.request import RequestWithSession


class TestRequestWithSession:
    @pytest.fixture()
    def request_session(self):
        """session fixture"""
        session = RequestWithSession()
        session.MAX_RETRY = 1
        session.DELAY = 0
        return session

    @staticmethod
    def gen_response(return_status, return_value):
        response = Response()
        response.status_code = return_status
        response.encoding = 'utf8'
        response._content = json.dumps(return_value).encode('utf-8')
        return response

    @pytest.mark.parametrize(
        'method, url, return_status, return_value',
        [
            ('GET', 'https://www.example.com', 200, {'message': 'ok'}),
            ('POST', 'https://www.example.com', 200, {'message': 'ok'}),
            ('POST', 'https://www.example.com', 400, {})
        ]
    )
    def test_request(self, request_session, mocker, method, url, return_status, return_value):
        """test request"""

        request = mocker.patch.object(Session, 'request', return_value=self.gen_response(return_status, return_value))
        resp = request_session.request(method, url)
        assert resp == return_value
        request.assert_called_once()
