"""Views do domínio de alunos."""

import json
from typing import Any

import httpx
from django.http import HttpResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.alunos import services
from apps.alunos.serializers import (
    AlunoInformacoesSerializer,
    AlunoPorCodigoSerializer,
    NecessidadeEspecialSerializer,
    TurmaDoAlunoSerializer,
)
from apps.core.responses import Response, detail_response

_TAG = ["Alunos"]
_MSG_CODIGO_OBRIGATORIO = "E necessario informar o codigo do aluno."
_MSG_CODIGOS_ALUNOS_OBRIGATORIOS = "Os códigos dos Alunos são obrigatórios."
_MSG_SIDECAR_INDISPONIVEL = "Servico de alunos indisponivel."


def _sidecar_error_response(exc: httpx.HTTPStatusError) -> Response:
    try:
        body: Any = exc.response.json()
    except ValueError:
        detail = exc.response.text.strip() or exc.response.reason_phrase
        body = {"detail": detail}
    return Response(body, status=exc.response.status_code)


def _sidecar_unavailable_response(_exc: httpx.RequestError) -> Response:
    return Response(
        {"detail": _MSG_SIDECAR_INDISPONIVEL},
        status=503,
    )


def _is_not_found(exc: httpx.HTTPStatusError) -> bool:
    return exc.response.status_code == 404


def _legacy_status_601_response(message: str) -> HttpResponse:
    response = HttpResponse(
        json.dumps(message, ensure_ascii=False),
        content_type="application/json",
    )
    response.status_code = 601
    return response


class AlunoInformacoesView(APIView):
    """Retorna informações completas do aluno."""

    @extend_schema(
        tags=_TAG,
        summary="Informações do aluno",
        description="Retorna informações completas do aluno pelo código.",
        responses={200: AlunoInformacoesSerializer, 204: None},
    )
    def get(self, _request: Request, codigo_aluno: str) -> Response:
        if not codigo_aluno.strip():
            return detail_response(_MSG_CODIGO_OBRIGATORIO)
        try:
            data = services.get_informacoes_aluno(codigo_aluno)
        except httpx.HTTPStatusError as exc:
            if _is_not_found(exc):
                return Response(status=204)
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        if data is None:
            return Response(status=204)
        return Response(AlunoInformacoesSerializer(data).data)


class AlunoNecessidadesEspeciaisView(APIView):
    """Retorna necessidades especiais do aluno."""

    @extend_schema(
        tags=_TAG,
        summary="Necessidades especiais do aluno",
        description="Retorna lista de necessidades especiais do aluno.",
        responses={200: NecessidadeEspecialSerializer},
    )
    def get(self, _request: Request, codigo_aluno: str) -> Response:
        if not codigo_aluno.strip():
            return detail_response(_MSG_CODIGO_OBRIGATORIO)
        try:
            data = services.get_necessidades_especiais_aluno(codigo_aluno)
        except httpx.HTTPStatusError as exc:
            if _is_not_found(exc):
                return Response(status=204)
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        if not data:
            return Response(status=204)
        if isinstance(data, list):
            data = data[0] if data else None
        if data is None:
            return Response(status=204)
        return Response(NecessidadeEspecialSerializer(data).data)


class AlunoTurmasView(APIView):
    """Retorna turmas do aluno."""

    @extend_schema(exclude=True)
    def get(self, _request: Request, codigo_aluno: str) -> Response:
        if not codigo_aluno.strip():
            return detail_response(_MSG_CODIGO_OBRIGATORIO)
        try:
            data = services.get_turmas_aluno(codigo_aluno)
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(TurmaDoAlunoSerializer(data, many=True).data)


class AlunoTurmasLegadoView(APIView):
    """Retorna turmas do aluno com os parâmetros do contrato legado."""

    @extend_schema(exclude=True)
    def get(self, _request: Request, **kwargs: str) -> Response:
        codigo_aluno = kwargs.get("codigoAluno")
        if codigo_aluno is None:
            return detail_response(_MSG_CODIGO_OBRIGATORIO)
        if not codigo_aluno.strip():
            return detail_response(_MSG_CODIGO_OBRIGATORIO)
        try:
            data = services.get_turmas_aluno(
                codigo_aluno,
                ano_letivo=kwargs.get("anoLetivo"),
                historico=kwargs.get("historico"),
                filtrar_situacao=kwargs.get("filtrarSituacao"),
                tipo_turma=kwargs.get("tipoTurma"),
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(TurmaDoAlunoSerializer(data, many=True).data)


class AlunosListView(APIView):
    """Lista alunos."""

    @extend_schema(
        tags=_TAG,
        summary="Lista de alunos",
        description="Retorna lista de alunos.",
        parameters=[
            OpenApiParameter(
                "codigos_aluno",
                int,
                OpenApiParameter.QUERY,
                many=True,
                required=False,
            )
        ],
        responses={200: AlunoPorCodigoSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        codigos_aluno = request.query_params.getlist(
            "codigos_aluno"
        ) or request.query_params.getlist("codigosAluno")
        if not codigos_aluno:
            return _legacy_status_601_response(
                _MSG_CODIGOS_ALUNOS_OBRIGATORIOS
            )
        try:
            data = services.listar_alunos(codigos_aluno)
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(AlunoPorCodigoSerializer(data, many=True).data)
