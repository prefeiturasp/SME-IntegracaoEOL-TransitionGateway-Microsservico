"""Views do domínio de matrículas."""

from collections import Counter
from typing import Any

import httpx
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.alunos import services as alunos_services
from apps.core.responses import Response, api_unavailable_response, detail_response
from apps.core.utils import get_first_value
from apps.institucional import services as institucional_services
from apps.core.views import DomainAPIView

from apps.matriculas import services
from apps.matriculas.serializers import (
    MatriculaAlunoEscolaSerializer,
    MatriculaSerializer,
    QuantidadeAlunosPorTurmaEscolaSerializer,
)

_TAG = ["Aluno"]
_MSG_ANO_LETIVO_INVALIDO = "ano_letivo deve ser um inteiro válido."
_DOMINIO_MATRICULAS = "matriculas"
_MSG_CODIGO_UE_OBRIGATORIO = "Código da UE obrigatório."
_MSG_CODIGO_DRE_OBRIGATORIO = "Código da DRE obrigatório."
_MSG_CODIGO_ESCOLA_OBRIGATORIO = "Código da escola obrigatório."
_MSG_CODIGO_ESCOLA_ALUNO_OBRIGATORIO = (
    "O código da escola e do aluno são obrigatórios"
)
_TIPO_TURNO_DESCRICAO = {
    1: "Manhã",
    2: "Intermediário",
    3: "Tarde",
    4: "Vespertino",
    5: "Noite",
    6: "Integral",
}


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
    return api_unavailable_response(_DOMINIO_MATRICULAS)


class MatriculasAPIView(DomainAPIView):
    """APIView base que padroniza falhas de comunicação com matrículas."""

    api_domain = _DOMINIO_MATRICULAS


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


def _to_int(value: Any) -> int | None:
    """Converte valores escalares para inteiro quando possível.

    Args:
        value: Valor a converter.

    Returns:
        Inteiro convertido ou ``None`` quando não for possível converter.
    """
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _ano_letivo_corrente() -> str:
    """Retorna o ano letivo corrente no fuso da aplicação."""
    return str(timezone.localdate().year)


def _extrair_codigo_ue(item: Any) -> str | None:
    """Extrai código de UE de objetos heterogêneos retornados por sidecars.

    Args:
        item: Item retornado por serviço institucional.

    Returns:
        Código da UE quando disponível, caso contrário ``None``.
    """
    if isinstance(item, str) and item.strip():
        return item.strip()
    if not isinstance(item, dict):
        return None
    value = get_first_value(
        item,
        "codigo_ue",
        "codigoUE",
        "ueCodigo",
        "codigo_eol",
        "codigoEol",
        "codigoEolEscola",
        "codigo_escola",
        "codigoEscola",
    )
    if value is None:
        return None
    codigo = str(value).strip()
    return codigo or None


def _extrair_codigos_ue_dre(data: Any) -> list[str]:
    """Extrai lista única de UEs de payloads por DRE.

    Args:
        data: Payload retornado pelo serviço institucional.

    Returns:
        Lista de códigos de UE sem duplicidade e preservando ordem.
    """
    if isinstance(data, dict):
        codigos = data.get("codigos_ue")
        if isinstance(codigos, list):
            data = codigos
        else:
            data = [data]
    if not isinstance(data, list):
        return []

    vistos: set[str] = set()
    resultado: list[str] = []
    for item in data:
        codigo = _extrair_codigo_ue(item)
        if not codigo or codigo in vistos:
            continue
        vistos.add(codigo)
        resultado.append(codigo)
    return resultado


def _agregar_turnos_por_ue(alunos: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Agrega totais por turno no formato legado esperado por M03.

    Args:
        alunos: Lista de alunos da UE no ano letivo.

    Returns:
        Objeto do contrato legado M03, ou ``None`` quando não houver dados.
    """
    totais_por_turno: Counter[int] = Counter()
    matriculas_contadas: set[str] = set()

    for indice, aluno in enumerate(alunos):
        if not isinstance(aluno, dict):
            continue

        situacao = _to_int(
            get_first_value(
                aluno,
                "codigo_situacao_matricula",
                "codigoSituacaoMatricula",
            )
        )
        if situacao != 1:
            continue

        tipo_turno = _to_int(get_first_value(aluno, "tipo_turno", "tipoTurno"))
        if tipo_turno is None:
            continue

        codigo_matricula = get_first_value(
            aluno,
            "codigo_matricula",
            "codigoMatricula",
        )
        chave_matricula = (
            str(codigo_matricula)
            if codigo_matricula is not None
            else f"linha:{indice}:{tipo_turno}"
        )
        if chave_matricula in matriculas_contadas:
            continue
        matriculas_contadas.add(chave_matricula)
        totais_por_turno[tipo_turno] += 1

    if not totais_por_turno:
        return None

    turnos = [
        {
            "turno": _TIPO_TURNO_DESCRICAO.get(tipo_turno, str(tipo_turno)),
            "tipoTurno": tipo_turno,
            "quantidade": quantidade,
        }
        for tipo_turno, quantidade in sorted(totais_por_turno.items())
    ]
    total = sum(totais_por_turno.values())
    return {
        "totalMatricula": total,
        "turnos": turnos,
    }


def _fallback_total_matriculas_por_turno_ue(ue_codigo: str) -> dict[str, Any] | None:
    """Monta M03 a partir da listagem de alunos por UE/ano corrente.

    Args:
        ue_codigo: Código da unidade educacional.

    Returns:
        Payload legado M03 ou ``None`` quando não houver dados.
    """
    alunos = alunos_services.get_alunos_da_ue(ue_codigo, _ano_letivo_corrente())
    if not isinstance(alunos, list) or not alunos:
        return None
    return _agregar_turnos_por_ue(alunos)


def _fallback_total_matriculas_por_turno_dre(dre_codigo: str) -> list[dict[str, Any]]:
    """Monta M04 agregando M03 para todas as UEs da DRE.

    Args:
        dre_codigo: Código da DRE.

    Returns:
        Lista no contrato legado M04.
    """
    escolas = institucional_services.get_ues_por_dre(dre_codigo)
    codigos_ue = _extrair_codigos_ue_dre(escolas)
    resposta: list[dict[str, Any]] = []

    for codigo_ue in codigos_ue:
        agregado_ue = _fallback_total_matriculas_por_turno_ue(codigo_ue)
        if not agregado_ue:
            continue
        resposta.append(
            {
                "codigoEolEscola": codigo_ue,
                "totalMatriculas": agregado_ue["totalMatricula"],
                "turnos": agregado_ue["turnos"],
            }
        )
    return resposta


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


class MatriculasAnosAnterioresView(MatriculasAPIView):
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


class TotalMatriculasPorTurnoUeView(MatriculasAPIView):
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
            if not data:
                data = _fallback_total_matriculas_por_turno_ue(ue_codigo)
        except httpx.HTTPStatusError as exc:
            return _api_error_response(exc)
        except httpx.RequestError as exc:
            return _api_unavailable_response(exc)
        if not data:
            return Response(status=204)
        return Response(data)


class TotalMatriculasPorTurnoDreView(MatriculasAPIView):
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
            if not data:
                data = _fallback_total_matriculas_por_turno_dre(dre_codigo)
        except httpx.HTTPStatusError as exc:
            return _api_error_response(exc)
        except httpx.RequestError as exc:
            return _api_unavailable_response(exc)
        if not data:
            return Response(status=204)
        return Response(data)


class QuantidadeAlunosPorTurmaEscolaView(MatriculasAPIView):
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


class MatriculasAlunoEscolaView(MatriculasAPIView):
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
