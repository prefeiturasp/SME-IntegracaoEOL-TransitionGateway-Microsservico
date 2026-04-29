"""ContextVars para request ID e nome do serviço no pipeline de logging."""

from __future__ import annotations

import logging
from contextvars import ContextVar

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
service_ctx: ContextVar[str] = ContextVar("service", default="unknown")


def get_request_id() -> str:
    """Retorna o request ID atual ou '-' se não definido."""
    request_id = request_id_ctx.get()
    return request_id or "-"


class ContextFilter(logging.Filter):
    """Injeta request_id e service em cada registro de log."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        record.service = service_ctx.get()
        return True
