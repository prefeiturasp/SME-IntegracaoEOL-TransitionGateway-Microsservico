"""Views do domínio de matrículas."""

from typing import Any

import httpx
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.core.responses import Response, detail_response
from apps.matriculas import services
from apps.matriculas.serializers import MatriculaSerializer

_TAG = ["Alunos"]
_MSG_ANO_LETIVO_INVALIDO = "ano_letivo deve ser um inteiro válido."
_MSG_SIDECAR_INDISPONIVEL = "Servico de matriculas indisponivel."


def _sidecar_error_response(exc: httpx.HTTPStatusError) -> Response:
    """Monta resposta do gateway para erro HTTP do sidecar.

    Args:
        exc: Exceção HTTP lançada pelo cliente do sidecar.

    Returns:
        Resposta com o corpo e status retornados pelo sidecar.
    """
    try:
        body: Any = exc.response.json()
    except ValueError:
        detail = exc.response.text.strip() or exc.response.reason_phrase
        body = {"detail": detail}
    return Response(body, status=exc.response.status_code)


def _sidecar_unavailable_response(_exc: httpx.RequestError) -> Response:
    """Monta resposta de indisponibilidade do sidecar.

    Args:
        _exc: Exceção de comunicação com o sidecar.

    Returns:
        Resposta de indisponibilidade no formato do gateway.
    """
    return Response({"detail": _MSG_SIDECAR_INDISPONIVEL}, status=503)


def _query_alias(request: Request, *names: str) -> str | None:
    """Lê o primeiro alias preenchido da query string.

    Args:
        request: Requisição HTTP recebida.
        *names: Nomes aceitos para o mesmo parâmetro.

    Returns:
        Valor recebido, ou ``None`` quando nenhum alias estiver preenchido.
    """
    for name in names:
        value = request.query_params.get(name)
        if value:
            return str(value)
    return None


class MatriculasAnoAtualView(APIView):
    """Lista matrículas consolidadas do ano letivo."""

    @extend_schema(
        tags=_TAG,
        summary="Matrículas consolidadas do ano letivo",
        description="Retorna quantidade de matrículas por turma de uma UE.",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.QUERY),
            OpenApiParameter("anoLetivo", int, OpenApiParameter.QUERY),
            OpenApiParameter("ue_codigo", str, OpenApiParameter.QUERY),
            OpenApiParameter("ueCodigo", str, OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, request: Request) -> Response:
        """Busca matrículas consolidadas por ano letivo e UE.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Matrículas consolidadas por turma.
        """
        ano_raw = _query_alias(request, "ano_letivo", "anoLetivo")
        ue_codigo = _query_alias(request, "ue_codigo", "ueCodigo")
        if not ano_raw or not ue_codigo:
            # Réplica do legado: parâmetros ausentes zeram o binding e a
            # consulta responde 200 com lista vazia.
            # TODO(149612): quando o contrato legado for descontinuado,
            # responder 400 exigindo ano_letivo e ue_codigo.
            return Response([])
        try:
            ano_letivo = int(ano_raw)
        except (TypeError, ValueError):
            return detail_response(_MSG_ANO_LETIVO_INVALIDO)
        try:
            data = services.get_matriculas_ano_atual(
                ano_letivo=ano_letivo,
                ue_codigo=ue_codigo,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(MatriculaSerializer(data, many=True).data)
