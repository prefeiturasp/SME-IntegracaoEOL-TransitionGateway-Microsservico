"""Fábricas de respostas HTTP reutilizáveis."""

from rest_framework.response import Response

__all__ = ["Response", "detail_response"]


def detail_response(detail: str, status_code: int = 400) -> Response:
    """Retorna uma resposta padronizada com campo `detail`.

    Args:
        detail: Mensagem de detalhe enviada no corpo da resposta.
        status_code: Código de status HTTP da resposta.

    Returns:
        Resposta com o corpo `{"detail": detail}` e o status informado.
    """
    return Response({"detail": detail}, status=status_code)
