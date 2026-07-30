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
from apps.matriculas.serializers import (
    MatriculaAlunoEscolaSerializer,
    MatriculaSerializer,
    QuantidadeAlunosPorTurmaEscolaSerializer,
)

_TAG = ["Aluno"]
_MSG_ANO_LETIVO_INVALIDO = "ano_letivo deve ser um inteiro válido."
_MSG_API_INDISPONIVEL = "Servico de matriculas indisponivel."
_MSG_CODIGO_UE_OBRIGATORIO = "Código da UE obrigatório."
_MSG_CODIGO_DRE_OBRIGATORIO = "Código da DRE obrigatório."
_MSG_CODIGO_ESCOLA_OBRIGATORIO = "Código da escola obrigatório."
_MSG_CODIGO_ESCOLA_ALUNO_OBRIGATORIO = (
    "O código da escola e do aluno são obrigatórios"
)


def _api_error_response(exc: httpx.HTTPStatusError) -> Response:
    """Monta resposta do gateway para erro HTTP da API.

    Args:
        exc: Exceção HTTP lançada pelo cliente da API.

    Returns:
        Resposta com o corpo e status retornados pela API.
    """
    try:
        body: Any = exc.response.json()
    except ValueError:
        detail = exc.response.text.strip() or exc.response.reason_phrase
        body = {"detail": detail}
    return Response(body, status=exc.response.status_code)


def _api_unavailable_response(_exc: httpx.RequestError) -> Response:
    """Monta resposta de indisponibilidade da API.

    Args:
        _exc: Exceção de comunicação com a API.

    Returns:
        Resposta de indisponibilidade no formato do gateway.
    """
    return Response({"detail": _MSG_API_INDISPONIVEL}, status=503)


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
            OpenApiParameter("ue_codigo", str, OpenApiParameter.QUERY),
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
        ano_raw = _query_alias(request, "ano_letivo")
        ue_codigo = _query_alias(request, "ue_codigo")
        if not ano_raw or not ue_codigo:
            # Réplica do legado: parâmetros ausentes zeram o binding e a
            # consulta responde 200 com lista vazia.
            # TODO(149612): exigir ano_letivo e ue_codigo  # NOSONAR
            # quando o contrato legado for descontinuado.
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
            return _api_error_response(exc)
        except httpx.RequestError as exc:
            return _api_unavailable_response(exc)
        return Response(MatriculaSerializer(data, many=True).data)


class MatriculasAnosAnterioresView(APIView):
    """Lista matrículas históricas consolidadas por turma."""

    @extend_schema(
        tags=_TAG,
        summary="Matrículas consolidadas de anos anteriores",
        description="Retorna quantidade histórica de matrículas por turma.",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.QUERY),
            OpenApiParameter("ue_codigo", str, OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, request: Request) -> Response:
        """Busca matrículas históricas por ano letivo e UE.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Matrículas históricas consolidadas por turma.
        """
        ano_raw = _query_alias(request, "ano_letivo")
        ue_codigo = _query_alias(request, "ue_codigo")
        if not ano_raw or not ue_codigo:
            return Response([])
        try:
            ano_letivo = int(ano_raw)
        except (TypeError, ValueError):
            return detail_response(_MSG_ANO_LETIVO_INVALIDO)
        try:
            data = services.get_matriculas_anos_anteriores(
                ano_letivo=ano_letivo,
                ue_codigo=ue_codigo,
            )
        except httpx.HTTPStatusError as exc:
            return _api_error_response(exc)
        except httpx.RequestError as exc:
            return _api_unavailable_response(exc)
        return Response(MatriculaSerializer(data, many=True).data)


class TotalMatriculasPorTurnoUeView(APIView):
    """Lista o total de matrículas por turno na UE."""

    @extend_schema(
        tags=_TAG,
        summary="Total de matrículas por turno na UE",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
        ],
        responses={200: OpenApiResponse(description="Success"), 204: None},
    )
    def get(self, _request: Request, ue_codigo: str) -> Response:
        """Busca total de matrículas por turno da UE.

        Args:
            _request: Requisição HTTP recebida.
            ue_codigo: Código da unidade educacional.

        Returns:
            Objeto com total de matrículas e turnos quando houver dados ou
            204 quando não houver registros.
        """
        if not ue_codigo.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        try:
            data = services.get_total_matriculas_por_turno_ue(ue_codigo)
        except httpx.HTTPStatusError as exc:
            return _api_error_response(exc)
        except httpx.RequestError as exc:
            return _api_unavailable_response(exc)
        if not data:
            return Response(status=204)
        return Response(data)


class TotalMatriculasPorTurnoDreView(APIView):
    """Lista o total de matrículas por turno na DRE."""

    @extend_schema(
        tags=_TAG,
        summary="Total de matrículas por turno na DRE",
        parameters=[
            OpenApiParameter("dre_codigo", str, OpenApiParameter.PATH),
        ],
        responses={200: OpenApiResponse(description="Success"), 204: None},
    )
    def get(self, _request: Request, dre_codigo: str) -> Response:
        """Busca total de matrículas por turno da DRE.

        Args:
            _request: Requisição HTTP recebida.
            dre_codigo: Código da DRE.

        Returns:
            Lista com totais por escola quando houver dados, ou 204 quando
            não houver registros.
        """
        if not dre_codigo.strip():
            return detail_response(_MSG_CODIGO_DRE_OBRIGATORIO)
        try:
            data = services.get_total_matriculas_por_turno_dre(dre_codigo)
        except httpx.HTTPStatusError as exc:
            return _api_error_response(exc)
        except httpx.RequestError as exc:
            return _api_unavailable_response(exc)
        if not data:
            return Response(status=204)
        return Response(data)


class QuantidadeAlunosPorTurmaEscolaView(APIView):
    """Lista a quantidade de alunos por turma na escola."""

    @extend_schema(
        tags=_TAG,
        summary="Quantidade de alunos por turma na escola",
        parameters=[
            OpenApiParameter("codigo_escola", str, OpenApiParameter.PATH),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, _request: Request, codigo_escola: str) -> Response:
        """Busca quantidade de alunos por turma da escola.

        Args:
            _request: Requisição HTTP recebida.
            codigo_escola: Código da escola.

        Returns:
            Quantidades agregadas por turma no contrato legado. Quando não
            houver dados, retorna 200 com lista vazia.
        """
        if not codigo_escola.strip():
            return detail_response(_MSG_CODIGO_ESCOLA_OBRIGATORIO)
        try:
            data = services.get_quantidade_alunos_por_turma_escola(
                codigo_escola
            )
        except httpx.HTTPStatusError as exc:
            return _api_error_response(exc)
        except httpx.RequestError as exc:
            return _api_unavailable_response(exc)
        return Response(
            QuantidadeAlunosPorTurmaEscolaSerializer(data, many=True).data
        )


class MatriculasAlunoEscolaView(APIView):
    """Lista matrículas de um aluno na escola."""

    @extend_schema(
        tags=_TAG,
        summary="Matrículas de um aluno na escola",
        parameters=[
            OpenApiParameter("codigo_escola", str, OpenApiParameter.PATH),
            OpenApiParameter("codigo_aluno", int, OpenApiParameter.PATH),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(
        self,
        _request: Request,
        codigo_escola: str,
        codigo_aluno: str,
    ) -> Response:
        """Busca matrículas de um aluno na escola.

        Args:
            _request: Requisição HTTP recebida.
            codigo_escola: Código da escola.
            codigo_aluno: Código EOL do aluno.

        Returns:
            Matrículas do aluno na escola no contrato legado. Quando não
            houver dados, retorna 200 com lista vazia.
        """
        if not codigo_escola.strip() or not codigo_aluno.strip():
            return detail_response(_MSG_CODIGO_ESCOLA_ALUNO_OBRIGATORIO)
        try:
            int(codigo_aluno)
        except (TypeError, ValueError):
            return detail_response(_MSG_CODIGO_ESCOLA_ALUNO_OBRIGATORIO)
        try:
            data = services.get_matriculas_aluno_escola(
                codigo_escola,
                codigo_aluno,
            )
        except httpx.HTTPStatusError as exc:
            return _api_error_response(exc)
        except httpx.RequestError as exc:
            return _api_unavailable_response(exc)
        return Response(MatriculaAlunoEscolaSerializer(data, many=True).data)
