"""Fábricas de respostas HTTP reutilizáveis."""

from typing import Any

import httpx
from rest_framework.response import Response

__all__ = [
    "Response",
    "api_unavailable_response",
    "detail_response",
    "api_error_response_status_livre",
]


def api_unavailable_response(domain: str, status_code: int = 503) -> Response:
    """Retorna resposta padronizada para API temporariamente indisponível."""
    return detail_response(f"Serviço de {domain} indisponível.", status_code)


def detail_response(detail: str, status_code: int = 400) -> Response:
    """Retorna uma resposta padronizada com campo `detail`."""
    return Response({"detail": detail}, status=status_code)


def api_error_response_status_livre(
    exc: httpx.HTTPStatusError,
) -> Response:
    """Monta resposta de erro preservando status fora do intervalo padrão.

    O legado usa códigos como 601, acima do limite aceito na construção da
    resposta; por isso o código é atribuído depois.

    Args:
        exc: Exceção HTTP lançada pelo cliente externo.

    Returns:
        Resposta com o corpo e o status originais da API.
    """
    try:
        body: Any = exc.response.json()
    except ValueError:
        detail = exc.response.text.strip() or exc.response.reason_phrase
        body = {"detail": detail}
    resposta = Response(body, status=400)
    resposta.status_code = exc.response.status_code
    return resposta
