"""ContextVars para request ID e nome do serviço no pipeline de logging."""

from __future__ import annotations

import logging
from contextvars import ContextVar

import elasticapm

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
service_ctx: ContextVar[str] = ContextVar("service", default="unknown")


def get_request_id() -> str:
    """Retorna o request ID atual ou '-' se não definido."""
    return request_id_ctx.get() or "-"


class ContextFilter(logging.Filter):
    """Injeta request_id, service e IDs de rastreamento APM em cada log."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get() or "-"
        record.service = service_ctx.get()
        record.transaction_id = elasticapm.get_transaction_id() or "-"
        record.trace_id = elasticapm.get_trace_id() or "-"
        return True
