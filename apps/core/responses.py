"""Fábricas de respostas HTTP reutilizáveis."""

from rest_framework.response import Response

__all__ = ["Response", "detail_response"]


def detail_response(detail: str, status_code: int = 400) -> Response:
    """Retorna uma resposta padronizada com campo `detail`."""
    return Response({"detail": detail}, status=status_code)
