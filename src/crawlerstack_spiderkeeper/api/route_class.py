import json
from typing import Callable, Dict

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.datastructures import UploadFile

from crawlerstack_spiderkeeper.schemas.audit import AuditCreate
from crawlerstack_spiderkeeper.services import audit_service


class AuditRoute(APIRoute):
    AUDIT_METHOD = [
        'PUT',
        'POST',
        'DELETE'
    ]

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response = await original_route_handler(request)
            if self.should_audit(request):
                await self.audit_record(request, response)
            return response

        return custom_route_handler

    def should_audit(self, request: Request) -> bool:
        if request.method in self.AUDIT_METHOD:
            return True
        return False

    async def audit_record(self, request: Request, response: Response):
        try:
            user = request.user
        except AssertionError:
            user = None

        query_params = request.query_params
        response_media_type = response.media_type

        if 'json' in response.media_type:
            response_body = json.loads(response.body.decode(response.charset))
        else:
            response_body = self.get_request_body(request)

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
        await audit_service.create(obj_in=AuditCreate(**data))

    async def get_request_body(self, request: Request) -> Dict:
        """
        提取 request 对象中的 body 信息，请求信息可能是 form 表单或者是 json
        :param request:
        :return:
        """
        body = {}
        form = await request.form()
        if form:
            for k, v in form.items():
                if isinstance(v, UploadFile):
                    v = {
                        'name': v.filename,
                        'type': 'file',
                        'content_type': v.content_type
                    }
                body.update({k: v})
        else:
            body_bytes = await request.body()
            if body_bytes:
                body = request.json()
        return body
