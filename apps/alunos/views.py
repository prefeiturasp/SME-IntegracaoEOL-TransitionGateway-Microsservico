"""Views do domínio de alunos."""

import json
from datetime import datetime
from typing import Any, cast

import httpx
from django.http import HttpResponse
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.alunos import services
from apps.alunos.serializers import (
    AlunoAtivoTurmaSerializer,
    AlunoAutocompleteSerializer,
    AlunoInformacoesSerializer,
    AlunoMatriculaTurmaSerializer,
    AlunoPorCodigoSerializer,
    DadosAcompanhamentoEscolarSerializer,
    FiliacaoResponsavelSerializer,
    InformacoesAlunoTurmaSerializer,
    NecessidadeEspecialSerializer,
    QuantidadeMatriculadosCCSerializer,
    QuantidadeMatriculadosSerializer,
    ResponsavelResumidoSerializer,
    TurmaDoAlunoSerializer,
)
from apps.core.responses import (
    Response,
    detail_response,
    sidecar_error_response_status_livre,
)

_TAG = ["Aluno"]
_MSG_CODIGO_OBRIGATORIO = "É necessário informar o codigo do aluno."
_MSG_CODIGO_TURMA_OBRIGATORIO = "É necessário informar o codigo da turma."
_MSG_CODIGO_UE_OBRIGATORIO = "É necessário informar o codigo da UE."
_MSG_CODIGOS_ALUNOS_OBRIGATORIOS = "Os códigos dos Alunos são obrigatórios."
_MSG_NOME_ALUNO_MINIMO = "O Nome deve conter no mínimo 3 caracteres."
_MSG_CPF_RESPONSAVEL_INVALIDO = "CPF do responsável inválido."
_MSG_CODIGO_TURMA_LEGADO = "O código da turma é obrigatório."
_MSG_DATA_TICKS_OBRIGATORIA = (
    "O código da turma e data da aula são obrigatórios"
)
_MSG_SIDECAR_INDISPONIVEL = "Servico de alunos indisponivel."
_MSG_LEGADO_ERRO_INESPERADO = (
    "Houve um comportamento inesperado do sistema. Por favor, contate a SME."
)
_EXEMPLO_BOOL_LEGADO = OpenApiExample("Padrão do legado", value=True)


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


def _inteiro_positivo(value: str) -> bool:
    """Verifica se o valor representa um inteiro positivo.

    Args:
        value: Texto que será validado.

    Returns:
        `True` quando o valor representar um inteiro positivo.
    """
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


def _legacy_string_response(message: str, status_code: int) -> Response:
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
    return cast(Response, response)


def _legacy_status_601_response(message: str) -> Response:
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


def _path_bool(value: str) -> bool | None:
    """Normaliza booleano recebido no path."""
    normalized = value.lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None


class AlunoAutocompleteAtivosView(APIView):
    """Lista alunos ativos para autocomplete."""

    @extend_schema(
        tags=_TAG,
        summary="Autocomplete de alunos ativos",
        description="Retorna alunos ativos de uma UE por filtro.",
        parameters=[
            OpenApiParameter("ue_codigo", str, OpenApiParameter.PATH),
            OpenApiParameter("aluno_nome", str, OpenApiParameter.QUERY),
            OpenApiParameter("data_referencia", str, OpenApiParameter.QUERY),
            OpenApiParameter("aluno_codigo", int, OpenApiParameter.QUERY),
            OpenApiParameter(
                "limite",
                int,
                OpenApiParameter.QUERY,
                default=10,
            ),
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
        if _query_value(request, "data_referencia") is None:
            # Réplica do legado: dataReferencia é obrigatório no binding do
            # ASP.NET e a ausência falha antes de qualquer outra validação.
            # TODO(149612): tratar dataReferencia como opcional  # NOSONAR
            # quando o contrato legado for descontinuado.
            return _legacy_string_response(_MSG_LEGADO_ERRO_INESPERADO, 400)
        if not ue_codigo.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        aluno_nome = _query_value(request, "aluno_nome")
        aluno_nome = aluno_nome.strip() if aluno_nome is not None else None
        try:
            aluno_codigo = _query_int_alias(request, 0, "aluno_codigo")
            limite = _query_int(request, "limite", 10)
            data_referencia = _query_datetime_alias(request, "data_referencia")
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


class AlunoAutocompleteUeView(APIView):
    """Lista alunos da UE/ano para autocomplete."""

    @extend_schema(
        tags=_TAG,
        summary="Autocomplete de alunos da UE por ano letivo",
        description="Retorna alunos da UE no ano letivo por filtro.",
        parameters=[
            OpenApiParameter("codigo_ue", str, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigos_turmas", int, OpenApiParameter.QUERY, many=True
            ),
            OpenApiParameter("nome_aluno", str, OpenApiParameter.QUERY),
            OpenApiParameter("codigo_eol", str, OpenApiParameter.QUERY),
            OpenApiParameter("somente_ativos", bool, OpenApiParameter.QUERY),
            OpenApiParameter("eh_historico", bool, OpenApiParameter.QUERY),
            OpenApiParameter(
                "limite",
                int,
                OpenApiParameter.QUERY,
                default=10,
            ),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(
        self, request: Request, codigo_ue: str, ano_letivo: str
    ) -> Response:
        """Busca alunos da UE no ano letivo para autocomplete.

        Args:
            request: Requisição HTTP recebida.
            codigo_ue: Código EOL da unidade educacional.
            ano_letivo: Ano letivo consultado.

        Returns:
            Alunos encontrados compatíveis com os filtros.
        """
        try:
            limite = _query_int(request, "limite", 10)
        except ValueError as exc:
            return detail_response(str(exc))
        codigo_turmas = request.query_params.getlist("codigos_turmas")
        try:
            data = services.get_alunos_autocomplete_ue(
                codigo_ue=codigo_ue,
                ano_letivo=ano_letivo,
                codigo_turmas=codigo_turmas,
                nome_aluno=_query_value(request, "nome_aluno"),
                codigo_eol=_query_value(request, "codigo_eol"),
                somente_ativos=_query_value(request, "somente_ativos"),
                eh_historico=_query_value(request, "eh_historico"),
                limite=limite,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(AlunoAutocompleteSerializer(data, many=True).data)


class DadosAcompanhamentoEscolarView(APIView):
    """Lista dados de acompanhamento escolar dos alunos."""

    @extend_schema(
        tags=_TAG,
        summary="Dados de acompanhamento escolar",
        description=(
            "Retorna dados dos alunos para acompanhamento do estudante."
        ),
        parameters=[
            OpenApiParameter("codigo_aluno", int, OpenApiParameter.QUERY),
            OpenApiParameter("codigo_dre", str, OpenApiParameter.QUERY),
            OpenApiParameter("codigo_ue", str, OpenApiParameter.QUERY),
            OpenApiParameter("cpf_responsavel", str, OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, request: Request) -> Response:
        """Busca dados de acompanhamento escolar conforme os filtros.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Dados de acompanhamento escolar dos alunos.
        """
        try:
            data = services.get_dados_acompanhamento_escolar(
                codigo_aluno=_query_value(request, "codigo_aluno"),
                codigo_dre=_query_value(request, "codigo_dre"),
                codigo_ue=_query_value(request, "codigo_ue"),
                cpf_responsavel=_query_value(request, "cpf_responsavel"),
            )
        except httpx.HTTPStatusError as exc:
            return sidecar_error_response_status_livre(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(
            DadosAcompanhamentoEscolarSerializer(data, many=True).data
        )


class AlunoTurmasComHistoricoView(APIView):
    """Lista turmas do aluno com origem histórica explícita."""

    @extend_schema(
        tags=_TAG,
        summary="Turmas do aluno por histórico, situação e tipo de turma",
        description=(
            "Retorna as turmas do aluno no ano letivo, escolhendo a origem "
            "(corrente ou histórica) e os filtros de situação e tipo."
        ),
        parameters=[
            OpenApiParameter("codigo_aluno", int, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("historico", bool, OpenApiParameter.PATH),
            OpenApiParameter(
                "filtrar_situacao",
                bool,
                OpenApiParameter.PATH,
                default=True,
                examples=[_EXEMPLO_BOOL_LEGADO],
            ),
            OpenApiParameter(
                "tipo_turma",
                bool,
                OpenApiParameter.PATH,
                default=True,
                examples=[_EXEMPLO_BOOL_LEGADO],
            ),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(
        self,
        _request: Request,
        codigo_aluno: str,
        ano_letivo: str,
        historico: str,
        filtrar_situacao: str,
        tipo_turma: str,
    ) -> Response:
        """Busca turmas do aluno conforme origem e filtros informados.

        Args:
            codigo_aluno: Código EOL do aluno.
            ano_letivo: Ano letivo consultado.
            historico: Consulta os vínculos históricos quando verdadeiro.
            filtrar_situacao: Restringe às situações de matrícula válidas.
            tipo_turma: Exclui turmas do tipo programa quando verdadeiro.

        Returns:
            Lista de turmas do aluno conforme os filtros.
        """
        if not codigo_aluno.strip():
            return detail_response(_MSG_CODIGO_OBRIGATORIO)
        try:
            data = services.get_turmas_aluno_com_historico(
                codigo_aluno,
                ano_letivo,
                historico,
                filtrar_situacao,
                tipo_turma,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(TurmaDoAlunoSerializer(data, many=True).data)


class AlunosPorAnoView(APIView):
    """Lista alunos pelos códigos restritos a um ano letivo."""

    @extend_schema(
        tags=_TAG,
        summary="Alunos por códigos e ano letivo",
        description="Retorna alunos pelos códigos no ano letivo informado.",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigos_aluno",
                int,
                OpenApiParameter.QUERY,
                many=True,
                required=True,
            ),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, request: Request, ano_letivo: str) -> Response:
        """Lista alunos pelos códigos informados no ano letivo.

        Args:
            request: Requisição HTTP recebida.
            ano_letivo: Ano letivo consultado.

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
            data = services.listar_alunos_por_ano(ano_letivo, codigos_aluno)
        except httpx.HTTPStatusError as exc:
            return sidecar_error_response_status_livre(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(AlunoPorCodigoSerializer(data, many=True).data)


class QuantidadeMatriculadosCCView(APIView):
    """Lista matriculados por componente curricular e ano letivo."""

    @extend_schema(
        tags=_TAG,
        summary="Matriculados por componente curricular",
        description=(
            "Retorna quantidades de matriculados por componente curricular."
        ),
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("dre_id", str, OpenApiParameter.QUERY),
            OpenApiParameter("ue_id", str, OpenApiParameter.QUERY),
            OpenApiParameter(
                "componentes_curriculares",
                int,
                OpenApiParameter.QUERY,
                many=True,
                required=True,
            ),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, request: Request, ano_letivo: str) -> Response:
        """Busca matriculados por componente conforme os filtros.

        Args:
            request: Requisição HTTP recebida.
            ano_letivo: Ano letivo consultado.

        Returns:
            Quantidades de matriculados por componente curricular.
        """
        componentes = request.query_params.getlist(
            "componentes_curriculares"
        ) or request.query_params.getlist("componentesCurriculares")
        try:
            data = services.get_quantidade_matriculados_cc(
                ano_letivo=ano_letivo,
                componentes_curriculares=componentes,
                dre_id=_query_value(request, "dre_id"),
                ue_id=_query_value(request, "ue_id"),
            )
        except httpx.HTTPStatusError as exc:
            return sidecar_error_response_status_livre(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(
            QuantidadeMatriculadosCCSerializer(data, many=True).data
        )


class QuantidadeMatriculadosView(APIView):
    """Lista a quantidade de alunos matriculados por ano letivo."""

    @extend_schema(
        tags=_TAG,
        summary="Quantidade de alunos matriculados",
        description=(
            "Retorna quantidades de matriculados agregadas por turma."
        ),
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("dre_codigo", str, OpenApiParameter.QUERY),
            OpenApiParameter("ue_codigo", str, OpenApiParameter.QUERY),
            OpenApiParameter(
                "modalidade", int, OpenApiParameter.QUERY, many=True
            ),
            OpenApiParameter("ano", int, OpenApiParameter.QUERY, many=True),
            OpenApiParameter("turma", int, OpenApiParameter.QUERY, many=True),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, request: Request, ano_letivo: str) -> Response:
        """Busca a quantidade de matriculados conforme os filtros.

        Args:
            request: Requisição HTTP recebida.
            ano_letivo: Ano letivo consultado.

        Returns:
            Quantidades de matriculados agregadas por turma.
        """
        try:
            data = services.get_quantidade_matriculados(
                ano_letivo=ano_letivo,
                dre_codigo=_query_value(request, "dre_codigo"),
                ue_codigo=_query_value(request, "ue_codigo"),
                modalidade=request.query_params.getlist("modalidade"),
                ano=request.query_params.getlist("ano"),
                turma=request.query_params.getlist("turma"),
            )
        except httpx.HTTPStatusError as exc:
            return sidecar_error_response_status_livre(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(
            QuantidadeMatriculadosSerializer(data, many=True).data
        )


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
                # Réplica do legado: não encontrado responde 204.
                # TODO(149612): responder 404 aqui  # NOSONAR
                # quando o contrato legado for descontinuado.
                return Response(status=204)
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        if data is None:
            # TODO(149612): responder 404 aqui  # NOSONAR
            # quando o contrato legado for descontinuado.
            return Response(status=204)
        return Response(ResponsavelResumidoSerializer(data).data)


class FiliacaoAlunoView(APIView):
    """Lista os dados de filiação do aluno."""

    @extend_schema(
        tags=_TAG,
        summary="Filiação do aluno",
        description="Retorna os responsáveis de filiação do aluno.",
        parameters=[
            OpenApiParameter("codigo_aluno", int, OpenApiParameter.PATH),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, _request: Request, codigo_aluno: str) -> Response:
        """Busca os dados de filiação do aluno.

        Args:
            codigo_aluno: Código EOL do aluno.

        Returns:
            Lista de responsáveis de filiação do aluno.
        """
        try:
            int(codigo_aluno)
        except (TypeError, ValueError):
            return detail_response(_MSG_CODIGO_OBRIGATORIO)
        try:
            data = services.get_filiacao_aluno(codigo_aluno)
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(FiliacaoResponsavelSerializer(data, many=True).data)


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
            # TODO(149612): responder 400 aqui  # NOSONAR
            # quando o contrato legado for descontinuado.
            return _legacy_string_response(_MSG_CODIGO_TURMA_LEGADO, 601)
        if codigo_int < 0:
            # Réplica do legado: turma negativa consulta e retorna vazio.
            # TODO(149612): responder 400 aqui  # NOSONAR
            # quando o contrato legado for descontinuado.
            return Response([])
        try:
            data = services.get_informacoes_alunos_turma(codigo_turma)
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(InformacoesAlunoTurmaSerializer(data, many=True).data)


class AlunosAtivosDataAulaTicksView(APIView):
    """Lista alunos ativos de uma turma na data da aula."""

    @extend_schema(
        tags=["Turma"],
        description=(
            "Retorna os alunos da turma na data da aula informada (ticks "
            "de DateTime do .NET no path)."
        ),
        parameters=[
            OpenApiParameter(
                "codigo_turma",
                int,
                OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                "data_ticks",
                int,
                OpenApiParameter.PATH,
            ),
        ],
        responses={200: AlunoMatriculaTurmaSerializer(many=True)},
    )
    def get(
        self,
        _request: Request,
        codigo_turma: str,
        data_ticks: str,
    ) -> Response:
        """Retorna os alunos da turma na data da aula informada.

        Args:
            _request: Requisição HTTP recebida.
            codigo_turma: Código EOL da turma.
            data_ticks: Data de referência em ticks de DateTime do .NET.

        Returns:
            Lista de alunos no contrato legado. Retorna lista vazia quando o
            código da turma não for positivo e erro 400 quando os ticks
            forem inválidos.
        """
        if not _inteiro_positivo(codigo_turma):
            return Response([])
        if not _inteiro_positivo(data_ticks):
            return detail_response(_MSG_DATA_TICKS_OBRIGATORIA)
        try:
            data = services.get_alunos_ativos_data_aula_ticks(
                codigo_turma=codigo_turma,
                data_ticks=data_ticks,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        data = [{**aluno, "numero_aluno_chamada": "000"} for aluno in data]
        serializer = AlunoMatriculaTurmaSerializer(data, many=True)
        return Response(serializer.data)


class AlunosDataMatriculaTicksView(APIView):
    """Lista alunos de uma turma por data de matricula."""

    @extend_schema(
        tags=["Turma"],
        description=(
            "Retorna os alunos da turma na data de matricula informada "
            "(ticks de DateTime do .NET no path)."
        ),
        parameters=[
            OpenApiParameter(
                "codigo_turma",
                int,
                OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                "data_matricula_ticks",
                int,
                OpenApiParameter.PATH,
            ),
        ],
        responses={200: AlunoMatriculaTurmaSerializer(many=True)},
    )
    def get(
        self,
        _request: Request,
        codigo_turma: str,
        data_matricula_ticks: str,
    ) -> Response:
        """Lista alunos de uma turma por data de matricula."""
        if not _inteiro_positivo(codigo_turma):
            return Response([])
        if not _inteiro_positivo(data_matricula_ticks):
            return detail_response(_MSG_DATA_TICKS_OBRIGATORIA)

        try:
            data = services.get_alunos_data_matricula_ticks(
                codigo_turma=codigo_turma,
                data_matricula_ticks=data_matricula_ticks,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)

        serializer = AlunoMatriculaTurmaSerializer(
            data,
            many=True,
            campos_parciais=True,
            datetime_z=False,
        )
        return Response(serializer.data)


class AlunoTurmaConsideraInativosView(APIView):
    """Retorna dados de um aluno em uma turma."""

    @extend_schema(
        tags=["Turma"],
        description=(
            "Retorna dados de aluno e matricula da turma, considerando "
            "matriculas inativas conforme indicador informado."
        ),
        parameters=[
            OpenApiParameter(
                "codigo_turma",
                int,
                OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                "codigo_aluno",
                int,
                OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                "considera_inativos",
                bool,
                OpenApiParameter.PATH,
            ),
        ],
        responses={200: AlunoMatriculaTurmaSerializer, 204: None},
    )
    def get(
        self,
        _request: Request,
        codigo_turma: str,
        codigo_aluno: str,
        considera_inativos: str,
    ) -> Response:
        """Retorna dados de um aluno em uma turma."""
        try:
            codigo_turma_int = int(codigo_turma)
            int(codigo_aluno)
        except (TypeError, ValueError):
            return _legacy_string_response(_MSG_LEGADO_ERRO_INESPERADO, 400)

        if codigo_turma_int <= 0:
            return Response(status=204)

        considera_inativos_bool = _path_bool(considera_inativos)
        if considera_inativos_bool is None:
            return detail_response(
                "Parametro 'considera_inativos' deve ser true ou false."
            )

        try:
            data = services.get_alunos_por_turma(
                codigo_turma,
                considerar_inativos=considera_inativos_bool,
                codigo_aluno=codigo_aluno,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)

        if not data:
            return Response(status=204)
        return Response(AlunoMatriculaTurmaSerializer(data[0]).data)


class AlunoMatriculasTurmaView(APIView):
    """Lista as matrículas de um aluno em uma turma."""

    @extend_schema(
        tags=["Turma"],
        description=(
            "Retorna as matrículas do aluno na turma informada, "
            "considerando também matrículas inativas."
        ),
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter("codigo_aluno", int, OpenApiParameter.PATH),
        ],
        responses={200: AlunoMatriculaTurmaSerializer(many=True)},
    )
    def get(
        self,
        _request: Request,
        codigo_turma: str,
        codigo_aluno: str,
    ) -> Response:
        """Lista as matrículas do aluno na turma informada.

        Args:
            _request: Requisição HTTP recebida.
            codigo_turma: Código EOL da turma.
            codigo_aluno: Código EOL do aluno.

        Returns:
            Lista de matrículas do aluno na turma, ou lista vazia quando
            não houver correspondência.
        """
        try:
            int(codigo_turma)
            int(codigo_aluno)
        except (TypeError, ValueError):
            return _legacy_string_response(_MSG_LEGADO_ERRO_INESPERADO, 400)

        try:
            data = services.get_alunos_por_turma(
                codigo_turma,
                considerar_inativos=True,
                codigo_aluno=codigo_aluno,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)

        return Response(AlunoMatriculaTurmaSerializer(data, many=True).data)


class AlunosCalculoFrequenciaTurmaView(APIView):
    """Lista os códigos de aluno de uma turma para cálculo de frequência."""

    @extend_schema(
        tags=["Turma"],
        description=(
            "Retorna os códigos dos alunos vinculados à turma (vigentes e "
            "históricos), usados como base para o cálculo de frequência."
        ),
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, _request: Request, codigo_turma: str) -> Response:
        """Lista os códigos de aluno da turma para cálculo de frequência.

        Args:
            _request: Requisição HTTP recebida.
            codigo_turma: Código EOL da turma.

        Returns:
            Lista de códigos de aluno (string, contrato legado), ou lista
            vazia quando a turma não tiver alunos.

        Nota:
            O legado une matrícula vigente e histórica com uma condição
            extra (`nr_chamada_aluno` nulo + `dt_situacao_aluno` anterior
            ao início da turma) que este endpoint não reproduz ainda — ver
            151517-endpoints-turmas.md.
        """
        if not codigo_turma.strip():
            return detail_response(_MSG_CODIGO_TURMA_OBRIGATORIO)
        try:
            data = services.get_alunos_por_turma(
                codigo_turma, considerar_inativos=True
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        # O UNION (distinct) não tem ORDER BY, mas o SQL Server devolve o
        # resultado ordenado ascendente como efeito colateral da
        # deduplicação. Espelhamos: dedup + ordenação numérica ascendente.
        codigos = sorted(
            {str(aluno["codigo_aluno"]) for aluno in data}, key=int
        )
        return Response(codigos)


def _query_int_list(request: Request, nome: str) -> list[int]:
    """Extrai inteiros repetíveis da query string, ignorando inválidos.

    Args:
        request: Requisição consultada.
        nome: Nome do parâmetro (snake_case).

    Returns:
        Inteiros informados, sem entradas vazias ou não numéricas.
    """
    valores: list[int] = []
    for bruto in request.query_params.getlist(nome):
        texto = bruto.strip()
        if texto.lstrip("-").isdigit():
            valores.append(int(texto))
    return valores


def _query_int_opt(request: Request, nome: str) -> int | None:
    """Lê um inteiro opcional da query string.

    Args:
        request: Requisição consultada.
        nome: Nome do parâmetro (snake_case).

    Returns:
        Inteiro informado, ou ``None`` quando ausente/inválido.
    """
    bruto = request.query_params.get(nome)
    if bruto is not None and bruto.strip().lstrip("-").isdigit():
        return int(bruto.strip())
    return None


class CodigosTurmasRegularesAlunoView(APIView):
    """Lista códigos de turma regulares do aluno no ano letivo."""

    @extend_schema(
        tags=["Turma"],
        description=(
            "Retorna os códigos de turma do aluno no ano letivo, "
            "resolvidos pelo Alunos-MS (situação de matrícula) e recortados "
            "pelo Pedagógico-MS (tipo de turma, UE e semestre)."
        ),
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("codigo_aluno", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "tipos_turma",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                many=True,
                required=False,
            ),
            OpenApiParameter(
                "ue_codigo", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "data_referencia", str, OpenApiParameter.QUERY, required=False
            ),
            OpenApiParameter(
                "semestre", int, OpenApiParameter.QUERY, required=False
            ),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(
        self,
        request: Request,
        ano_letivo: str,
        codigo_aluno: str,
    ) -> Response:
        """Lista os códigos de turma regulares do aluno no ano letivo.

        Args:
            request: Requisição com os filtros ``tipos_turma``, ``ue_codigo``,
                ``data_referencia`` e ``semestre``.
            ano_letivo: Ano letivo consultado.
            codigo_aluno: Código EOL do aluno.

        Returns:
            Lista de códigos de turma (inteiros), ou lista vazia quando não
            houver correspondência.
        """
        tipos_turma = _query_int_list(request, "tipos_turma")
        ue_codigo = request.query_params.get("ue_codigo")
        data_referencia = request.query_params.get("data_referencia")
        semestre = _query_int_opt(request, "semestre")
        try:
            codigos = services.montar_codigos_turmas_regulares_aluno(
                ano_letivo=ano_letivo,
                codigo_aluno=codigo_aluno,
                tipos_turma=tipos_turma,
                ue_codigo=ue_codigo,
                data_referencia=data_referencia,
                semestre=semestre,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        # Os códigos são devolvidos como string (IReadOnlyList<string>).
        return Response([str(codigo) for codigo in codigos])


class CodigoTurmaAlunoComponenteCurricularView(APIView):
    """Lista códigos de turma do aluno por componente curricular.

    Alias do endpoint ``.../regulares``: o componente curricular é aceito
    na rota mas ignorado no corpo do handler, consultando a mesma função.
    Aqui só ``tipos_turma`` é considerado, conforme a assinatura deste
    endpoint.
    """

    @extend_schema(
        tags=["Turma"],
        description=(
            "Retorna os códigos de turma do aluno no ano letivo. O código "
            "do componente curricular é aceito na rota mas ignorado."
        ),
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("codigo_aluno", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "componente_curricular_codigo",
                int,
                OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                "tipos_turma",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                many=True,
                required=False,
            ),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(
        self,
        request: Request,
        ano_letivo: str,
        codigo_aluno: str,
        componente_curricular_codigo: str,
    ) -> Response:
        """Lista os códigos de turma do aluno, ignorando o componente.

        Args:
            request: Requisição com o filtro ``tipos_turma``.
            ano_letivo: Ano letivo consultado.
            codigo_aluno: Código EOL do aluno.
            componente_curricular_codigo: Aceito na rota mas ignorado.

        Returns:
            Lista de códigos de turma (inteiros), ou lista vazia quando não
            houver correspondência.
        """
        tipos_turma = _query_int_list(request, "tipos_turma")
        try:
            codigos = services.montar_codigos_turmas_regulares_aluno(
                ano_letivo=ano_letivo,
                codigo_aluno=codigo_aluno,
                tipos_turma=tipos_turma,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        # Os códigos são devolvidos como string (IReadOnlyList<string>).
        return Response([str(codigo) for codigo in codigos])


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


class AlunosDaUeView(APIView):
    """Lista alunos matriculados em uma unidade educacional."""

    @extend_schema(
        tags=_TAG,
        summary="Alunos da UE por ano letivo",
        description="Retorna os alunos matriculados em uma UE no ano letivo.",
        parameters=[
            OpenApiParameter("codigo_ue", str, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("nome_aluno", str, OpenApiParameter.QUERY),
            OpenApiParameter("codigo_eol", str, OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(
        self,
        request: Request,
        codigo_ue: str,
        ano_letivo: str,
    ) -> Response:
        """Busca alunos matriculados em uma unidade educacional.

        Args:
            request: Requisição com filtros opcionais de aluno.
            codigo_ue: Código EOL da unidade educacional.
            ano_letivo: Ano letivo consultado.

        Returns:
            Lista de alunos da unidade educacional.
        """
        if not codigo_ue.strip() or not ano_letivo.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        try:
            data = services.get_alunos_da_ue(
                codigo_ue,
                ano_letivo,
                _query_value(request, "nome_aluno"),
                _query_value(request, "codigo_eol"),
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(AlunoPorCodigoSerializer(data, many=True).data)


class AlunoTurmasPorSituacaoView(APIView):
    """Lista turmas do aluno filtradas por situação de matrícula e tipo."""

    @extend_schema(
        tags=_TAG,
        summary="Turmas do aluno por situação de matrícula e tipo de turma",
        description=(
            "Retorna as turmas do aluno no ano letivo, filtrando por "
            "situação de matrícula e tipo de turma."
        ),
        parameters=[
            OpenApiParameter("codigo_aluno", int, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "filtrar_situacao_matricula",
                bool,
                OpenApiParameter.PATH,
                default=True,
                examples=[_EXEMPLO_BOOL_LEGADO],
            ),
            OpenApiParameter(
                "tipo_turma",
                bool,
                OpenApiParameter.PATH,
                default=True,
                examples=[_EXEMPLO_BOOL_LEGADO],
            ),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(
        self,
        _request: Request,
        codigo_aluno: str,
        ano_letivo: str,
        filtrar_situacao_matricula: str,
        tipo_turma: str,
    ) -> Response:
        """Busca turmas do aluno filtradas por situação e tipo de turma.

        Args:
            codigo_aluno: Código EOL do aluno.
            ano_letivo: Ano letivo consultado.
            filtrar_situacao_matricula: Indicador booleano de filtro.
            tipo_turma: Indicador booleano de tipo de turma.

        Returns:
            Lista de turmas do aluno conforme os filtros.
        """
        if not codigo_aluno.strip():
            return detail_response(_MSG_CODIGO_OBRIGATORIO)
        try:
            data = services.get_turmas_aluno_por_situacao(
                codigo_aluno,
                ano_letivo,
                filtrar_situacao_matricula,
                tipo_turma,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(TurmaDoAlunoSerializer(data, many=True).data)


class AlunosAtivosTurmaView(APIView):
    """Lista alunos ativos de uma turma."""

    @extend_schema(
        tags=_TAG,
        summary="Alunos ativos da turma",
        description="Retorna os alunos ativos de uma turma.",
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(self, _request: Request, codigo_turma: str) -> Response:
        """Busca os alunos ativos de uma turma.

        Args:
            codigo_turma: Código EOL da turma.

        Returns:
            Lista de alunos ativos da turma.
        """
        if not codigo_turma.strip():
            return detail_response(_MSG_CODIGO_TURMA_OBRIGATORIO)
        try:
            data = services.get_alunos_ativos_turma(codigo_turma)
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(AlunoAtivoTurmaSerializer(data, many=True).data)


class AlunosAtivosPeriodoTurmaView(APIView):
    """Lista alunos ativos de uma turma em um período."""

    @extend_schema(
        tags=_TAG,
        summary="Alunos ativos da turma por período",
        description="Retorna os alunos ativos da turma no período informado.",
        parameters=[
            OpenApiParameter("codigo_turma", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "data_referencia_fim", str, OpenApiParameter.PATH
            ),
            OpenApiParameter(
                "data_referencia_inicio", str, OpenApiParameter.QUERY
            ),
        ],
        responses={200: OpenApiResponse(description="Success")},
    )
    def get(
        self,
        request: Request,
        codigo_turma: str,
        data_referencia_fim: str,
    ) -> Response:
        """Busca alunos ativos da turma no período informado.

        Args:
            request: Requisição com a data inicial opcional.
            codigo_turma: Código EOL da turma.
            data_referencia_fim: Data final usada na consulta.

        Returns:
            Lista de alunos ativos da turma.
        """
        if not codigo_turma.strip():
            return detail_response(_MSG_CODIGO_TURMA_OBRIGATORIO)
        if not data_referencia_fim.strip():
            return detail_response(
                "É necessário informar a data de referência."
            )
        try:
            data = services.get_alunos_ativos_turma_periodo(
                codigo_turma,
                data_referencia_fim,
                _query_value(request, "data_referencia_inicio"),
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(AlunoAtivoTurmaSerializer(data, many=True).data)


class TotalAlunosAtivosPeriodoView(APIView):
    """Retorna o total de alunos ativos em um período."""

    @extend_schema(
        tags=_TAG,
        summary="Total de alunos ativos por período",
        description="Retorna a quantidade de alunos ativos no período.",
        parameters=[
            OpenApiParameter("ano_turma", str, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("data_inicio", str, OpenApiParameter.PATH),
            OpenApiParameter("data_fim", str, OpenApiParameter.PATH),
            OpenApiParameter("ue_id", str, OpenApiParameter.QUERY),
            OpenApiParameter("dre_id", str, OpenApiParameter.QUERY),
            OpenApiParameter(
                "modalidades", int, OpenApiParameter.QUERY, many=True
            ),
        ],
        responses={200: OpenApiTypes.INT},
    )
    def get(
        self,
        request: Request,
        ano_turma: str,
        ano_letivo: str,
        data_inicio: str,
        data_fim: str,
    ) -> Response:
        """Busca o total de alunos ativos no período informado.

        Args:
            request: Requisição com filtros opcionais de abrangência.
            ano_turma: Ano escolar usado no filtro.
            ano_letivo: Ano letivo consultado.
            data_inicio: Data inicial do período.
            data_fim: Data final do período.

        Returns:
            Quantidade de alunos ativos no período.
        """
        try:
            data = services.get_total_alunos_ativos_periodo(
                ano_turma=ano_turma,
                ano_letivo=ano_letivo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                ue_id=_query_value(request, "ue_id"),
                dre_id=_query_value(request, "dre_id"),
                modalidades=request.query_params.getlist("modalidades"),
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError as exc:
            return _sidecar_unavailable_response(exc)
        return Response(data["quantidade"])


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
