"""Middlewares de propagação de X-Request-ID e contexto de logging."""

from __future__ import annotations

import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from apps.core.logging_context import request_id_ctx, service_ctx


class RequestIDMiddleware:
    """Lê X-Request-ID do header (ou gera um UUID) e propaga na resposta."""

    def __init__(
        self, get_response: Callable[[HttpRequest], HttpResponse]
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.request_id = request_id  # type: ignore[attr-defined]
        token = request_id_ctx.set(request_id)
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)


class LoggingContextMiddleware:
    """Seta o nome do serviço no contexto de logging para cada request."""

    SERVICE_NAME = "transitiongateway"

    def __init__(
        self, get_response: Callable[[HttpRequest], HttpResponse]
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        service_token = service_ctx.set(self.SERVICE_NAME)
        try:
            return self.get_response(request)
        finally:
            service_ctx.reset(service_token)
