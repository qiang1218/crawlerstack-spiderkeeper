"""
Route class use to intercept messages.
"""
import json
from typing import Callable, Dict

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.datastructures import UploadFile

from crawlerstack_spiderkeeper.schemas.audit import AuditCreate
from crawlerstack_spiderkeeper.services import AuditService


class AuditRoute(APIRoute):
    """
    Audit route.
    """
    AUDIT_METHOD = [
        'PUT',
        'POST',
        'DELETE'
    ]

    def get_route_handler(self) -> Callable:
        """Intercept request in handler."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response = await original_route_handler(request)
            if self.should_audit(request):
                await _audit_record(request, response)
            return response

        return custom_route_handler

    def should_audit(self, request: Request) -> bool:
        """
        Check if the request need to be intercepted.
        :param request:
        :return:
        """
        if request.method in self.AUDIT_METHOD:
            return True
        return False


async def _audit_record(request: Request, response: Response):
    """
    Audit record, and save it.
    :param request:
    :param response:
    :return:
    """
    try:
        user = request.user
    except AssertionError:
        user = None

    query_params = request.query_params
    response_media_type = response.media_type

    if 'json' in response.media_type:
        response_body = json.loads(response.body.decode(response.charset))
    else:
        response_body = _get_request_body(request)

    detail = {
        'query_params': str(query_params),
        'response_media_type': response_media_type,
        'response_body': response_body
    }
    data = {
        'url': str(request.url),
        'method': request.method,
        'client': f'{request.client.host}:{request.client.port}',
        'user_id': user,
        'detail': json.dumps(detail),
    }
    db = request.app.extra.get('db')
    async with db.scoped_session() as session:
        service = AuditService(session)
        await service.create(obj_in=AuditCreate(**data))


async def _get_request_body(request: Request) -> Dict:
    """
    提取 request 对象中的 body 信息，请求信息可能是 form 表单或者是 json
    :param request:
    :return:
    """
    body = {}
    form = await request.form()
    if form:
        for key, value in form.items():
            if isinstance(value, UploadFile):
                value = {
                    'name': value.filename,
                    'type': 'file',
                    'content_type': value.content_type
                }
            body.update({key: value})
    else:
        body_bytes = await request.body()
        if body_bytes:
            body = request.json()
    return body
