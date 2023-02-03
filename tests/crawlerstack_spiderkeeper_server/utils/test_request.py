"""test reqeust"""
import json

import pytest
from httpx import Response as HttpxResponse
from requests import Response, Session

from crawlerstack_spiderkeeper_server.utils.request import (RequestWithHttpx,
                                                            RequestWithSession)


class TestRequestWithSession:
    """Test request with session"""

    @pytest.fixture()
    def request_session(self):
        """session fixture"""
        session = RequestWithSession()
        session.MAX_RETRY = 1
        session.DELAY = 0
        return session

    @staticmethod
    def gen_response(return_status, return_value):
        """get response"""
        response = Response()
        response.status_code = return_status
        response.encoding = 'utf8'
        response._content = json.dumps(return_value).encode('utf-8')  # pylint: disable=protected-access
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


class TestRequestWithHttpx:
    """Test request with httpx"""

    @pytest.fixture()
    def request_client(self):
        """Client fixture"""
        client = RequestWithHttpx()
        client.MAX_RETRY = 1
        client.DELAY = 0
        return client

    @staticmethod
    def gen_response(return_status, return_value):
        """get response"""
        response = HttpxResponse(status_code=return_status,content=json.dumps(return_value).encode('utf-8'))
        return response

    @pytest.mark.parametrize(
        'method, url, return_status, return_value',
        [
            ('GET', 'https://www.example.com', 200, {'message': 'ok'}),
            ('POST', 'https://www.example.com', 200, {'message': 'ok'}),
            ('POST', 'https://www.example.com', 400, {})
        ]
    )
    async def test_request(self, request_client, mocker, method, url, return_status, return_value):
        """test request"""
        request = mocker.patch.object(RequestWithHttpx, '_request',
                                      return_value=self.gen_response(return_status, return_value))
        resp = await request_client.request(method, url)
        assert resp == return_value
        request.assert_called_once()
