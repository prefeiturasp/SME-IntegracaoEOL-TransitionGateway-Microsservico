from __future__ import annotations

import uuid

from apps.core.logging_context import request_id_ctx, service_ctx


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.request_id = request_id
        token = request_id_ctx.set(request_id)
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)


class LoggingContextMiddleware:
    SERVICE_NAME = "transitiongateway"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        service_token = service_ctx.set(self.SERVICE_NAME)
        try:
            return self.get_response(request)
        finally:
            service_ctx.reset(service_token)
