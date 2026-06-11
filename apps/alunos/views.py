"""Views do domínio de alunos."""

import json
from datetime import datetime
from typing import Any

import httpx
from django.http import HttpResponse
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.alunos import services
from apps.alunos.serializers import (
    AlunoAutocompleteSerializer,
    AlunoInformacoesSerializer,
    AlunoPorCodigoSerializer,
    InformacoesAlunoTurmaSerializer,
    NecessidadeEspecialSerializer,
    ResponsavelResumidoSerializer,
    TurmaDoAlunoSerializer,
)
from apps.core.responses import Response, detail_response

_TAG = ["Alunos"]
_MSG_CODIGO_OBRIGATORIO = "É necessário informar o codigo do aluno."
_MSG_CODIGO_TURMA_OBRIGATORIO = "É necessário informar o codigo da turma."
_MSG_CODIGO_UE_OBRIGATORIO = "É necessário informar o codigo da UE."
_MSG_CODIGOS_ALUNOS_OBRIGATORIOS = "Os códigos dos Alunos são obrigatórios."
_MSG_NOME_ALUNO_MINIMO = "O Nome deve conter no mínimo 3 caracteres."
_MSG_CPF_RESPONSAVEL_INVALIDO = "CPF do responsável inválido."
_MSG_CODIGO_TURMA_LEGADO = "O código da turma é obrigatório."
_MSG_SIDECAR_INDISPONIVEL = "Servico de alunos indisponivel."
_MSG_LEGADO_ERRO_INESPERADO = (
    "Houve um comportamento inesperado do sistema. Por favor, contate a SME."
)


def _sidecar_error_response(exc: httpx.HTTPStatusError) -> Response:
    """Monta resposta de erro a partir da exceção HTTP recebida.

    Args:
        exc: Exceção HTTP lançada pelo cliente externo.

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
    return Response(
        {"detail": _MSG_SIDECAR_INDISPONIVEL},
        status=503,
    )


def _is_not_found(exc: httpx.HTTPStatusError) -> bool:
    """Verifica se a exceção representa recurso não encontrado."""
    return exc.response.status_code == 404


def _legacy_string_response(message: str, status_code: int) -> HttpResponse:
    """Monta resposta de texto puro no formato do contrato legado.

    Args:
        message: Mensagem serializada como string JSON no corpo.
        status_code: Código HTTP retornado pelo legado.

    Returns:
        Resposta HTTP idêntica à emitida pela API legada.
    """
    response = HttpResponse(
        json.dumps(message, ensure_ascii=False),
        content_type="application/json",
    )
    response.status_code = status_code
    return response


def _legacy_status_601_response(message: str) -> HttpResponse:
    """Monta resposta no formato esperado pelo contrato legado."""
    return _legacy_string_response(message, 601)


def _query_value(request: Request, *names: str) -> str | None:
    """Lê o primeiro alias preenchido da query string.

    Args:
        request: Requisição HTTP recebida.
        *names: Nomes aceitos para o mesmo parâmetro.

    Returns:
        Valor recebido, ou ``None`` quando nenhum alias estiver preenchido.
    """
    for name in names:
        raw = request.query_params.get(name)
        if raw not in (None, ""):
            return str(raw)
    return None


def _query_int(request: Request, name: str, default: int) -> int:
    """Lê um inteiro opcional da query string.

    Args:
        request: Requisição HTTP recebida.
        name: Nome do parâmetro de query.
        default: Valor usado quando o parâmetro estiver ausente.

    Returns:
        Valor convertido para inteiro.

    Raises:
        ValueError: Se o parâmetro não puder ser convertido.
    """
    raw = _query_value(request, name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Parâmetro '{name}' deve ser um inteiro válido."
        ) from exc


def _query_int_alias(request: Request, default: int, *names: str) -> int:
    """Lê inteiro opcional aceitando aliases de query string.

    Args:
        request: Requisição HTTP recebida.
        default: Valor usado quando nenhum alias estiver preenchido.
        *names: Nomes aceitos para o mesmo parâmetro.

    Returns:
        Valor convertido para inteiro.

    Raises:
        ValueError: Se algum alias preenchido não for inteiro válido.
    """
    raw = _query_value(request, *names)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Parâmetro '{names[0]}' deve ser um inteiro válido."
        ) from exc


def _query_datetime_alias(
    request: Request,
    *names: str,
) -> datetime | None:
    """Lê uma data/hora ISO opcional da query string.

    Args:
        request: Requisição HTTP recebida.
        *names: Nomes aceitos para o mesmo parâmetro.

    Returns:
        Valor convertido para data/hora, ou ``None`` quando ausente.

    Raises:
        ValueError: Se o parâmetro não for ISO válido.
    """
    raw = _query_value(request, *names)
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(
            f"Parâmetro '{names[0]}' deve ser uma data ISO 8601 válida."
        ) from exc


class AlunoAutocompleteAtivosView(APIView):
    """Lista alunos ativos para autocomplete."""

    @extend_schema(
        tags=_TAG,
        summary="Autocomplete de alunos ativos",
        description="Retorna alunos ativos de uma UE por filtro.",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
            OpenApiParameter("aluno_nome", str, OpenApiParameter.QUERY),
            OpenApiParameter("alunoNome", str, OpenApiParameter.QUERY),
            OpenApiParameter("data_referencia", str, OpenApiParameter.QUERY),
            OpenApiParameter("dataReferencia", str, OpenApiParameter.QUERY),
            OpenApiParameter("aluno_codigo", int, OpenApiParameter.QUERY),
            OpenApiParameter("alunoCodigo", int, OpenApiParameter.QUERY),
            OpenApiParameter("limite", int, OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, request: Request, ue_codigo: str) -> Response:
        """Busca alunos ativos para autocomplete.

        Args:
            request: Requisição HTTP recebida.
            ue_codigo: Código EOL da unidade educacional.

        Returns:
            Alunos encontrados compatíveis com os filtros.
        """
        if _query_value(request, "data_referencia", "dataReferencia") is None:
            # Réplica do legado: dataReferencia é obrigatório no binding do
            # ASP.NET e a ausência falha antes de qualquer outra validação.
            return _legacy_string_response(_MSG_LEGADO_ERRO_INESPERADO, 400)
        if not ue_codigo.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        aluno_nome = _query_value(request, "aluno_nome", "alunoNome")
        aluno_nome = aluno_nome.strip() if aluno_nome is not None else None
        try:
            aluno_codigo = _query_int_alias(
                request, 0, "aluno_codigo", "alunoCodigo"
            )
            limite = _query_int(request, "limite", 10)
            data_referencia = _query_datetime_alias(
                request, "data_referencia", "dataReferencia"
            )
        except ValueError as exc:
            return detail_response(str(exc))
        if aluno_codigo == 0 and len(aluno_nome or "") < 3:
            return detail_response(_MSG_NOME_ALUNO_MINIMO)
        try:
            data = services.buscar_alunos_ativos_autocomplete(
                ue_codigo=ue_codigo,
                aluno_nome=aluno_nome,
                data_referencia=data_referencia,
                aluno_codigo=aluno_codigo,
                limite=limite,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(AlunoAutocompleteSerializer(data, many=True).data)


class AlunoInformacoesView(APIView):
    """Retorna informações completas do aluno."""

    @extend_schema(
        tags=_TAG,
        summary="Informações do aluno",
        description="Retorna informações completas do aluno pelo código.",
        parameters=[
            OpenApiParameter(
                "codigo_aluno",
                int,
                OpenApiParameter.PATH,
            )
        ],
        responses={200: OpenApiResponse(description="Success"), 204: None},
    )
    def get(self, _request: Request, codigo_aluno: str) -> Response:
        """Busca informações cadastrais de um aluno.

        Args:
            codigo_aluno: Código EOL do aluno.

        Returns:
            Dados cadastrais do aluno.
        """
        try:
            codigo_int = int(codigo_aluno)
        except (ValueError, TypeError):
            return detail_response(_MSG_CODIGO_OBRIGATORIO)
        if codigo_int <= 0:
            return _legacy_status_601_response(_MSG_CODIGO_OBRIGATORIO)
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


class ResponsavelResumidoView(APIView):
    """Retorna dados resumidos de responsável."""

    @extend_schema(
        tags=_TAG,
        summary="Dados resumidos do responsável",
        description="Retorna dados resumidos de um responsável pelo CPF.",
        parameters=[
            OpenApiParameter(
                "cpf_responsavel",
                str,
                OpenApiParameter.PATH,
            )
        ],
        responses={200: OpenApiResponse(description="Success"), 204: None},
    )
    def get(self, _request: Request, cpf_responsavel: str) -> Response:
        """Busca dados resumidos de responsável.

        Args:
            cpf_responsavel: CPF do responsável.

        Returns:
            Dados resumidos do responsável, ou 204 quando não encontrado.
        """
        if not cpf_responsavel.isdigit():
            # Réplica do legado: CPF não numérico falha na consulta e
            # responde 400.
            return detail_response(_MSG_CPF_RESPONSAVEL_INVALIDO)
        try:
            data = services.get_responsavel_resumido(cpf_responsavel)
        except httpx.HTTPStatusError as exc:
            if _is_not_found(exc):
                return Response(status=204)
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        if data is None:
            return Response(status=204)
        return Response(ResponsavelResumidoSerializer(data).data)


class InformacoesAlunosTurmaView(APIView):
    """Lista informações dos alunos de uma turma."""

    @extend_schema(
        tags=_TAG,
        summary="Informações dos alunos da turma",
        description="Retorna resumo dos alunos da turma no formato diário.",
        parameters=[
            OpenApiParameter(
                "codigo_turma",
                int,
                OpenApiParameter.PATH,
            )
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, _request: Request, codigo_turma: str) -> Response:
        """Busca informações resumidas dos alunos de uma turma.

        Args:
            codigo_turma: Código EOL da turma.

        Returns:
            Lista de alunos da turma.
        """
        try:
            codigo_int = int(codigo_turma)
        except (ValueError, TypeError):
            return detail_response(_MSG_CODIGO_TURMA_OBRIGATORIO)
        if codigo_int == 0:
            # Réplica do legado: turma zero responde com o status 601.
            return _legacy_string_response(_MSG_CODIGO_TURMA_LEGADO, 601)
        if codigo_int < 0:
            # Réplica do legado: turma negativa consulta e retorna vazio.
            return Response([])
        try:
            data = services.get_informacoes_alunos_turma(codigo_turma)
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(InformacoesAlunoTurmaSerializer(data, many=True).data)


class AlunoNecessidadesEspeciaisView(APIView):
    """Retorna necessidades especiais do aluno."""

    @extend_schema(
        tags=_TAG,
        summary="Necessidades especiais do aluno",
        description="Retorna lista de necessidades especiais do aluno.",
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, _request: Request, codigo_aluno: str) -> Response:
        """Busca necessidades especiais do aluno.

        Args:
            codigo_aluno: Código EOL do aluno.

        Returns:
            Necessidade especial vinculada ao aluno.
        """
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
        """Retorna turmas do aluno.

        Args:
            codigo_aluno: Código EOL do aluno.

        Returns:
            Lista de turmas do aluno.
        """
        if not codigo_aluno.strip():
            return detail_response(_MSG_CODIGO_OBRIGATORIO)
        try:
            data = services.get_turmas_aluno(codigo_aluno)
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
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, request: Request) -> Response:
        """Lista alunos pelos códigos informados na query string.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Lista de alunos correspondentes aos códigos informados.
        """
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
