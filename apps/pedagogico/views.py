"""Views do domínio pedagógico."""

import json
from typing import Any, cast

import httpx
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.alunos.serializers import AlunoMatriculaTurmaSerializer
from apps.core.responses import detail_response
from apps.pedagogico import services
from apps.pedagogico.serializers import (
    AnosLetivosVigentesQuerySerializer,
    CodigoComponenteListSerializer,
    CodigoTurmaInteiroListSerializer,
    CodigoTurmaListSerializer,
    ComponenteBaseSerializer,
    ComponenteCurricularSerializer,
    ComponenteRegenciaSerializer,
    DadosAulaTurmaSerializer,
    GradeCurricularSerializer,
    ItinerarioEnsinoMedioSerializer,
    ListagemTurmasComponentesPaginadoSerializer,
    SincronizacaoInstitucionalTurmaSerializer,
    TurmaDadosSerializer,
    TurmaHistoricaGeralSerializer,
)

_TAG = ["ComponenteCurricular"]
_TAG_TURMA = ["Turma"]
_SERVICO_PEDAGOGICO_INDISPONIVEL = "Servico pedagogico indisponivel."
_RESPOSTA_SERVICO_PEDAGOGICO_INVALIDA = (
    "Resposta do servico pedagogico invalida."
)
_MSG_CODIGO_TURMA_UE_OBRIGATORIOS = "O código da turma e Ue são obrigatórios"
_TURMA_REQUEST_SCHEMA = {
    "type": "array",
    "items": {"type": "string"},
    "description": (
        "Body opcional com `codigos_turmas`; informe uma lista JSON de "
        "codigos de turmas."
    ),
}
_IDS_REQUEST_SCHEMA = {
    "type": "array",
    "items": {"type": "integer"},
    "description": "Lista JSON de `cod_agrupamento` de Território do Saber.",
}


def _obter_data_base_tick(request: Request) -> int | None:
    """Obtém o parâmetro de query `dataBaseTick` como inteiro.

    Args:
        request: Requisição HTTP recebida.

    Returns:
        Valor inteiro dos ticks do .NET, ou None quando ausente.

    Raises:
        ValueError: Quando `dataBaseTick` não for um inteiro válido.
    """
    bruto = request.query_params.get(
        "dataBaseTick", request.query_params.get("data_base_tick")
    )
    if bruto is None or bruto == "":
        return None
    return int(bruto)


def _inteiro_positivo(value: str) -> bool:
    """Verifica se o valor representa um inteiro positivo."""
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


def _ordem_numero_chamada(aluno: dict[str, Any]) -> tuple[int, int]:
    """Chave de ordenação ascendente por número de chamada do aluno.

    Args:
        aluno: Registro de aluno retornado pelo sidecar.

    Returns:
        Tupla em que registros sem número de chamada válido vêm primeiro e
        os números válidos são ordenados de forma ascendente pelo valor.
    """
    try:
        return (1, int(aluno["numero_aluno_chamada"]))
    except (KeyError, TypeError, ValueError):
        return (0, 0)


def _sidecar_error_response(exc: httpx.HTTPStatusError) -> Response:
    """Monta resposta de erro a partir da exceção HTTP recebida."""
    try:
        body = exc.response.json()
    except ValueError:
        detail = exc.response.text.strip() or exc.response.reason_phrase
        body = {"detail": detail}
    return Response(body, status=exc.response.status_code)


def _obter_lista_query(request: Request, nome: str) -> list[str]:
    """Obtém uma lista de valores de um parâmetro de query.

    Aceita parâmetros repetidos e o array JSON produzido por algumas versões
    do Swagger UI.

    Args:
        request: Requisição HTTP recebida.
        nome: Nome do parâmetro de query.

    Returns:
        Valores normalizados como lista de strings.
    """
    valores = cast(list[str], request.query_params.getlist(nome))
    if len(valores) != 1:
        return valores

    try:
        valor_json: Any = json.loads(valores[0])
    except (json.JSONDecodeError, TypeError):
        return valores

    if not isinstance(valor_json, list):
        return valores
    return [str(valor) for valor in valor_json]


class TurmasRegularesViewSet(APIView):
    """Lista turmas regulares existentes."""

    @extend_schema(
        tags=_TAG_TURMA,
        description=(
            "Retorna os codigos de turmas regulares encontradas.\n\n"
            "RequestBody: `codigos_turmas`."
        ),
        request={"application/json": _TURMA_REQUEST_SCHEMA},
        responses={200: CodigoTurmaListSerializer},
    )
    def post(self, request: Request) -> Response:
        """Retorna codigos de turmas regulares.

        Args:
            request: Requisicao HTTP com os codigos das turmas.

        Returns:
            Resposta HTTP com codigos de turmas regulares.

        Raises:
            httpx.HTTPError: Se a chamada ao servico pedagogico falhar.
            ValueError: Se a resposta do servico nao for JSON valido.
        """
        serializer = CodigoTurmaListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data:
            return Response([])

        data = services.post_turmas_regulares(serializer.validated_data)
        return Response(CodigoTurmaListSerializer(data).data)


class TurmasProgramaViewSet(APIView):
    """Lista turmas programa existentes."""

    @extend_schema(
        tags=_TAG_TURMA,
        description=(
            "Retorna os codigos de turmas programa encontradas.\n\n"
            "RequestBody: `codigos_turmas`."
        ),
        request={"application/json": _TURMA_REQUEST_SCHEMA},
        responses={200: CodigoTurmaListSerializer},
    )
    def post(self, request: Request) -> Response:
        """Retorna codigos de turmas programa.

        Args:
            request: Requisicao HTTP com os codigos das turmas.

        Returns:
            Resposta HTTP com codigos de turmas programa.

        Raises:
            httpx.HTTPError: Se a chamada ao servico pedagogico falhar.
            ValueError: Se a resposta do servico nao for JSON valido.
        """
        serializer = CodigoTurmaListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data:
            return Response([])

        data = services.post_turmas_programa(serializer.validated_data)
        return Response(CodigoTurmaListSerializer(data).data)


class ListarTurmasViewSet(APIView):
    """Lista dados de turmas existentes."""

    @extend_schema(
        tags=_TAG_TURMA,
        description="Retorna dados das turmas encontradas.",
        request={"application/json": _TURMA_REQUEST_SCHEMA},
        responses={200: TurmaDadosSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        """Retorna dados de turmas.

        Args:
            request: Requisicao HTTP com os codigos das turmas.

        Returns:
            Resposta HTTP com dados das turmas.

        Raises:
            httpx.HTTPError: Se a chamada ao servico pedagogico falhar.
            ValueError: Se a resposta do servico nao for JSON valido.
        """
        serializer = CodigoTurmaListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data:
            return Response([])

        data = services.post_listar_turmas(serializer.validated_data)
        return Response(TurmaDadosSerializer(data, many=True).data)


class DadosTurmaViewSet(APIView):
    """Retorna dados de uma turma."""

    @extend_schema(
        tags=_TAG_TURMA,
        description="Retorna dados da turma encontrada.",
        responses={200: TurmaDadosSerializer},
    )
    def get(self, _request: Request, codigo_turma: str) -> Response:
        """Retorna dados da turma.

        Args:
            _request: Requisicao HTTP recebida.
            codigo_turma: Codigo da turma.

        Returns:
            Resposta HTTP com dados da turma.

        Raises:
            httpx.HTTPError: Se a chamada ao servico pedagogico falhar.
            ValueError: Se a resposta do servico nao for JSON valido.
        """
        data = services.get_dados_turma(codigo_turma)
        return Response(TurmaDadosSerializer(data).data)


class AlunosAtivosTurmaSemRedisViewSet(APIView):
    """Lista alunos da turma reproduzindo o contrato legado sem Redis."""

    @extend_schema(
        tags=_TAG_TURMA,
        description=(
            "Retorna os alunos da turma alunos"
            "(somente ativos, primeira sequência)."
        ),
        parameters=[
            OpenApiParameter(
                "codigo_turma",
                int,
                OpenApiParameter.PATH,
            ),
        ],
        responses={200: AlunoMatriculaTurmaSerializer(many=True)},
    )
    def get(self, _request: Request, codigo_turma: str) -> Response:
        """Retorna os alunos da turma no contrato legado sem Redis.

        Args:
            _request: Requisição HTTP recebida.
            codigo_turma: Código EOL da turma.

        Returns:
            Lista de alunos no contrato legado, ou 204 quando o código da
            turma não for um inteiro positivo ou não houver alunos.
        """
        if not _inteiro_positivo(codigo_turma):
            return Response(status=204)
        try:
            data = services.get_alunos_ativos_turma_sem_redis(
                codigo_turma=codigo_turma,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError:
            return detail_response(_SERVICO_PEDAGOGICO_INDISPONIVEL, 503)
        if not data:
            return Response(status=204)
        data = sorted(data, key=_ordem_numero_chamada)
        serializer = AlunoMatriculaTurmaSerializer(
            data, many=True, campos_parciais=True, datetime_z=False
        )
        return Response(serializer.data)


class AlunosAtivosTurmaRedisMultplexViewSet(APIView):
    """Lista alunos da turma no contrato legado Redis Multplex."""

    @extend_schema(
        tags=_TAG_TURMA,
        description=(
            "Retorna os alunos da turma a partir do "
            "legado `ObterAlunosPorTurmaMultiplexConnetionAsync`."
        ),
        parameters=[
            OpenApiParameter(
                "codigo_turma",
                int,
                OpenApiParameter.PATH,
            ),
        ],
        responses={200: AlunoMatriculaTurmaSerializer(many=True)},
    )
    def get(self, _request: Request, codigo_turma: str) -> Response:
        """Retorna os alunos da turma no contrato legado Redis Multplex.

        Consome ``get_alunos_ativos_turma_redis_multplex``, que consulta o
        endpoint canônico do microsserviço de alunos sem ``data_aula_ticks``
        nem ``sequencia``, e serializa publicando todos os campos.

        Args:
            _request: Requisição HTTP recebida.
            codigo_turma: Código EOL da turma.

        Returns:
            Lista de alunos no contrato legado, ou 204 quando o código da
            turma não for um inteiro positivo ou não houver alunos.
        """
        if not _inteiro_positivo(codigo_turma):
            return Response(status=204)
        try:
            data = services.get_alunos_ativos_turma_redis_multplex(
                codigo_turma=codigo_turma,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError:
            return detail_response(_SERVICO_PEDAGOGICO_INDISPONIVEL, 503)
        if not data:
            return Response(status=204)
        data = sorted(data, key=_ordem_numero_chamada)
        serializer = AlunoMatriculaTurmaSerializer(data, many=True)
        return Response(serializer.data)


class AlunosTurmaConsideraInativosViewSet(APIView):
    """Lista alunos ativos de uma turma considerando ativos ou inativos."""

    @extend_schema(
        tags=_TAG_TURMA,
        description=(
            "Retorna alunos considerando ativos ou inativos da turma "
            "no contrato legado."
        ),
        parameters=[
            OpenApiParameter(
                "codigo_turma",
                int,
                OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                "considera_inativos",
                bool,
                OpenApiParameter.PATH,
            ),
        ],
        responses={200: AlunoMatriculaTurmaSerializer(many=True)},
    )
    def get(
        self,
        _request: Request,
        codigo_turma: str,
        considera_inativos: bool | None,
    ) -> Response:
        """Retorna os alunos da turma conforme o filtro de inatividade.

        Consome ``get_alunos_turma_considera_inativos``, que consulta o
        endpoint canônico do microsserviço de alunos repassando
        ``considerar_inativos`` e a primeira sequência. Serializa publicando
        todos os campos.

        Args:
            _request: Requisição HTTP recebida.
            codigo_turma: Código EOL da turma.
            considera_inativos: Inclui alunos inativos quando verdadeiro.

        Returns:
            Lista de alunos no contrato legado, ou 204 quando o código da
            turma não for um inteiro positivo.
        """
        if not _inteiro_positivo(codigo_turma):
            return Response(status=204)
        try:
            data = services.get_alunos_turma_considera_inativos(
                codigo_turma=codigo_turma,
                considera_inativos=considera_inativos,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError:
            return detail_response(_SERVICO_PEDAGOGICO_INDISPONIVEL, 503)
        serializer = AlunoMatriculaTurmaSerializer(data, many=True)
        return Response(serializer.data)


class TurmasHistoricasGeraisProfessorViewSet(APIView):
    """Lista turmas históricas gerais de um professor."""

    @extend_schema(
        tags=_TAG_TURMA,
        description=(
            "Retorna as turmas históricas gerais do professor no ano "
            "letivo informado."
        ),
        responses={200: TurmaHistoricaGeralSerializer(many=True)},
    )
    def get(
        self,
        _request: Request,
        ano_letivo: int,
        professor_rf: str,
    ) -> Response:
        """Retorna turmas históricas gerais do professor.

        Args:
            _request: Requisição HTTP recebida.
            ano_letivo: Ano letivo usado na consulta.
            professor_rf: Registro funcional do professor.

        Returns:
            Resposta HTTP com as turmas históricas encontradas.
        """
        try:
            data = services.get_turmas_historicas_gerais_professor(
                ano_letivo=ano_letivo,
                professor_rf=professor_rf,
            )
        except httpx.HTTPStatusError as exc:
            try:
                body = exc.response.json()
            except ValueError:
                detail = (
                    exc.response.text.strip() or exc.response.reason_phrase
                )
                body = {"detail": detail}
            return Response(body, status=exc.response.status_code)
        except httpx.RequestError:
            return detail_response(
                _SERVICO_PEDAGOGICO_INDISPONIVEL,
                503,
            )
        except ValueError:
            return detail_response(
                _RESPOSTA_SERVICO_PEDAGOGICO_INVALIDA,
                502,
            )

        serializer = TurmaHistoricaGeralSerializer(
            data=data,
            many=True,
        )
        if not serializer.is_valid():
            return detail_response(
                _RESPOSTA_SERVICO_PEDAGOGICO_INVALIDA,
                502,
            )
        return Response(serializer.data)


def _query_bool(request: Request, *nomes: str) -> bool:
    """Lê um booleano de query params.

    Args:
        request: Requisição HTTP recebida.
        nomes: Nomes de parâmetro aceitos, em ordem de precedência.

    Returns:
        Valor booleano interpretado do parâmetro (default False).
    """
    for nome in nomes:
        valor = request.query_params.get(nome)
        if valor is not None:
            return valor.lower() == "true"
    return False


def _query_int(request: Request, *nomes: str) -> int | None:
    """Lê um inteiro de query params.

    Args:
        request: Requisição HTTP recebida.
        nomes: Nomes de parâmetro aceitos, em ordem de precedência.

    Returns:
        Valor inteiro do parâmetro, ou None quando ausente/ inválido.
    """
    for nome in nomes:
        valor = request.query_params.get(nome)
        if valor:
            try:
                return int(valor)
            except ValueError:
                return None
    return None


class ListagemTurmasComponentesViewSet(APIView):
    """Lista turmas e componentes por UE, modalidade e ano letivo."""

    @extend_schema(
        tags=_TAG_TURMA,
        description=(
            "Retorna turmas e componentes por UE, modalidade e ano letivo"
        ),
        parameters=[
            OpenApiParameter(
                "codigoTurma", OpenApiTypes.INT, OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                "qtdeRegistros", OpenApiTypes.INT, OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                "qtdeRegistrosIgnorados",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                "ehProfessor", OpenApiTypes.BOOL, OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                "codigoRf", OpenApiTypes.STR, OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                "consideraHistorico",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                "periodoEscolarInicio",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                "anosInfantilDesconsiderar",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                many=True,
            ),
        ],
        responses={200: ListagemTurmasComponentesPaginadoSerializer},
    )
    def get(
        self,
        request: Request,
        codigo_ue: str,
        modalidade: int,
        ano_letivo: int,
    ) -> Response:
        """Lista turmas e componentes por UE, modalidade e ano letivo.

        Args:
            request: Requisição HTTP recebida.
            codigo_ue: Código da unidade educacional.
            modalidade: Código da modalidade de ensino.
            ano_letivo: Ano letivo consultado.

        Returns:
            Resposta HTTP com o envelope paginado de componentes.
        """
        eh_professor = _query_bool(
            request, "ehProfessor", "eh_professor"
        )
        codigo_rf = request.query_params.get(
            "codigoRf", request.query_params.get("codigo_rf")
        )
        anos_infantil = _obter_lista_query(
            request, "anosInfantilDesconsiderar"
        ) or _obter_lista_query(request, "anos_infantil_desconsiderar")
        try:
            data = services.get_listagem_turmas_componentes(
                codigo_ue=codigo_ue,
                modalidade=modalidade,
                ano_letivo=ano_letivo,
                codigo_turma=_query_int(
                    request, "codigoTurma", "codigo_turma"
                ),
                qtde_registros=_query_int(
                    request, "qtdeRegistros", "qtde_registros"
                ),
                qtde_registros_ignorados=_query_int(
                    request,
                    "qtdeRegistrosIgnorados",
                    "qtde_registros_ignorados",
                ),
                eh_professor=eh_professor,
                codigo_rf=codigo_rf if eh_professor else None,
                considera_historico=_query_bool(
                    request, "consideraHistorico", "considera_historico"
                ),
                periodo_escolar_inicio_tick=_query_int(
                    request, "periodoEscolarInicio", "periodo_escolar_inicio"
                ),
                anos_infantil_desconsiderar=anos_infantil,
            )
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError:
            return detail_response(_SERVICO_PEDAGOGICO_INDISPONIVEL, 503)
        except (ValueError, OverflowError):
            return detail_response(_RESPOSTA_SERVICO_PEDAGOGICO_INVALIDA, 502)

        serializer = ListagemTurmasComponentesPaginadoSerializer(data)
        return Response(serializer.data)


class SincronizacaoInstitucionalTurmaViewSet(APIView):
    """Retorna os dados institucionais de uma turma."""

    @extend_schema(
        tags=_TAG_TURMA,
        description="Retorna os dados institucionais sincronizados da turma.",
        responses={200: SincronizacaoInstitucionalTurmaSerializer},
    )
    def get(
        self,
        _request: Request,
        codigo_ue: str,
        codigo_turma: str,
    ) -> Response:
        """Retorna os dados institucionais da turma.

        Args:
            _request: Requisição HTTP recebida.
            codigo_ue: Código da unidade educacional.
            codigo_turma: Código da turma.

        Returns:
            Resposta HTTP com os dados institucionais da turma.
        """
        if not codigo_ue.strip() or not _inteiro_positivo(codigo_turma):
            return detail_response(_MSG_CODIGO_TURMA_UE_OBRIGATORIOS)

        try:
            data = services.get_sincronizacao_institucional_turma(
                codigo_ue=codigo_ue,
                codigo_turma=codigo_turma,
            )
        except httpx.HTTPStatusError as exc:
            try:
                body = exc.response.json()
            except ValueError:
                detail = (
                    exc.response.text.strip() or exc.response.reason_phrase
                )
                body = {"detail": detail}
            return Response(body, status=exc.response.status_code)
        except httpx.RequestError:
            return Response(
                {"detail": _SERVICO_PEDAGOGICO_INDISPONIVEL},
                status=503,
            )
        return Response(SincronizacaoInstitucionalTurmaSerializer(data).data)


class SincronizacoesInstitucionaisAnosLetivosViewSet(APIView):
    """Lista turmas institucionais da UE por anos letivos."""

    @extend_schema(
        tags=_TAG_TURMA,
        description=(
            "Retorna os códigos das turmas vinculadas às sincronizações "
            "institucionais da UE."
        ),
        parameters=[
            OpenApiParameter(
                name="anos_letivos_vigente",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
        ],
        responses={200: CodigoTurmaInteiroListSerializer},
    )
    def get(
        self,
        request: Request,
        codigo_ue: str,
    ) -> Response:
        """Lista códigos de turmas da UE.

        Args:
            request: Requisição HTTP recebida.
            codigo_ue: Código da unidade educacional.

        Returns:
            Resposta HTTP com os códigos das turmas encontradas.
        """
        query_serializer = AnosLetivosVigentesQuerySerializer(
            data={
                "anos_letivos_vigente": _obter_lista_query(
                    request,
                    "anos_letivos_vigente",
                )
            }
        )
        query_serializer.is_valid(raise_exception=True)
        anos = query_serializer.validated_data.get("anos_letivos_vigente")

        try:
            data = services.get_sincronizacoes_institucionais_anos_letivos(
                codigo_ue=codigo_ue,
                anos_letivos_vigente=anos or None,
            )
        except httpx.HTTPStatusError as exc:
            try:
                body = exc.response.json()
            except ValueError:
                detail = (
                    exc.response.text.strip() or exc.response.reason_phrase
                )
                body = {"detail": detail}
            return Response(body, status=exc.response.status_code)
        except httpx.RequestError:
            return Response(
                {"detail": _SERVICO_PEDAGOGICO_INDISPONIVEL},
                status=503,
            )

        return Response(CodigoTurmaInteiroListSerializer(data).data)


class ItinerariosEnsinoMedioViewSet(APIView):
    """Lista os itinerários do ensino médio."""

    @extend_schema(
        tags=_TAG_TURMA,
        description="Retorna os itinerários disponíveis no ensino médio.",
        responses={200: ItinerarioEnsinoMedioSerializer(many=True)},
    )
    def get(self, _request: Request) -> Response:
        """Retorna os itinerários do ensino médio.

        Args:
            _request: Requisição HTTP recebida.

        Returns:
            Resposta HTTP com os itinerários encontrados.
        """
        try:
            data = services.get_itinerarios_ensino_medio()
        except httpx.HTTPStatusError as exc:
            try:
                body = exc.response.json()
            except ValueError:
                detail = (
                    exc.response.text.strip() or exc.response.reason_phrase
                )
                body = {"detail": detail}
            return Response(body, status=exc.response.status_code)
        except httpx.RequestError:
            return detail_response(
                _SERVICO_PEDAGOGICO_INDISPONIVEL,
                503,
            )
        except ValueError:
            return detail_response(
                _RESPOSTA_SERVICO_PEDAGOGICO_INVALIDA,
                502,
            )

        serializer = ItinerarioEnsinoMedioSerializer(
            data=data,
            many=True,
        )
        if not serializer.is_valid():
            return detail_response(
                _RESPOSTA_SERVICO_PEDAGOGICO_INVALIDA,
                502,
            )
        return Response(serializer.validated_data)


class ComponentesCurricularesViewSet(APIView):
    """Lista componentes curriculares ativos."""

    @extend_schema(
        tags=_TAG,
        summary="Catálogo de componentes curriculares",
        description=(
            "Retorna todos os componentes curriculares ativos do EOL."
        ),
        responses={200: ComponenteBaseSerializer(many=True)},
    )
    def get(self, _request: Request) -> Response:
        """Retorna o catálogo de componentes curriculares.

        Args:
            _request: Requisição HTTP recebida.

        Returns:
            Resposta HTTP com os componentes curriculares ativos.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_curriculares()
        return Response(ComponenteBaseSerializer(data, many=True).data)


class ComponentesTurmaViewSet(APIView):
    """Lista componentes das turmas de uma UE."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes por lista de turmas e UE",
        description=(
            "Retorna componentes das turmas informadas, consolidando "
            "agrupamentos de Território do Saber. "
            "Componentes com `codigo=0` são descartados.\n\n"
        ),
        parameters=[
            OpenApiParameter(
                "turmas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
                description="Lista de códigos de turmas.",
            ),
        ],
        responses={200: ComponenteBaseSerializer(many=True)},
    )
    def get(self, request: Request, ue_id: str) -> Response:
        """Retorna componentes das turmas de uma UE.

        Args:
            request: Requisição HTTP com os códigos das turmas.
            ue_id: Código da unidade educacional.

        Returns:
            Resposta HTTP com os componentes encontrados.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_por_turmas_ue(
            ue_id=ue_id,
            turmas=request.query_params.getlist("turmas"),
        )
        return Response(ComponenteBaseSerializer(data, many=True).data)


class ComponentesTurmaProgramaViewSet(APIView):
    """Lista componentes de turmas programa."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes de turmas programa por UE e modalidade",
        description=(
            "Retorna componentes de turmas programa (projetos especiais) "
            "para UE + modalidade + ano letivo.\n\n"
            "**Modalidades:** 1=EI, 3=EJA, 4=CIEJA, 5=EF, 6=EM.\n\n"
        ),
        parameters=[
            OpenApiParameter(
                name="modalidade",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                enum=[1, 3, 4, 5, 6],
                description="Modalidades permitidas.",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(
        self, _request: Request, ue_id: str, modalidade: int, ano_letivo: int
    ) -> Response:
        """Retorna componentes de turmas programa.

        Args:
            _request: Requisição HTTP recebida.
            ue_id: Código da unidade educacional.
            modalidade: Modalidade de ensino.
            ano_letivo: Ano letivo.

        Returns:
            Resposta HTTP com os componentes de turmas programa.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_turmas_programa(
            ue_id=ue_id,
            modalidade=modalidade,
            ano_letivo=ano_letivo,
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesRegenciaViewSet(APIView):
    """Lista componentes de regência por ano de turma."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes de regência por ano de turma",
        description="Retorna componentes curriculares de regência.",
        responses={200: ComponenteRegenciaSerializer(many=True)},
    )
    def get(self, _request: Request, ano_turma: int) -> Response:
        """Retorna componentes de regência por ano de turma.

        Args:
            _request: Requisição HTTP recebida.
            ano_turma: Ano da turma.

        Returns:
            Resposta HTTP com os componentes de regência ou status 204.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_regencia(ano_turma)
        if data == []:
            return Response(status=204)
        return Response(ComponenteRegenciaSerializer(data, many=True).data)


class ValidarComponentePapViewSet(APIView):
    """Verifica se a turma possui componente curricular PAP."""

    @extend_schema(
        tags=_TAG,
        summary="Valida componente PAP por turma e funcionário",
        description="Verifica se a turma possui componente curricular PAP.",
        responses={200: OpenApiTypes.BOOL},
    )
    def get(
        self,
        _request: Request,
        codigo_turma: str,
        login: str,
        id_perfil: str,
    ) -> Response:
        """Valida se a turma possui componente PAP para o funcionário.

        Args:
            _request: Requisição HTTP recebida.
            codigo_turma: Código da turma.
            login: Login/RF do funcionário.
            id_perfil: Identificador do perfil.

        Returns:
            Resposta HTTP com o resultado booleano da validação.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.validar_componente_pap(
            codigo_turma=codigo_turma,
            login=login,
            id_perfil=id_perfil,
        )
        return Response(data)


class ComponentesFuncionarioViewSet(APIView):
    """Lista componentes curriculares do funcionário."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes curriculares por funcionário e perfil",
        description="Retorna componentes curriculares do funcionário.",
        responses={
            200: ComponenteCurricularSerializer(many=True),
            204: None,
        },
    )
    def get(
        self,
        _request: Request,
        login: str,
        id_perfil: str,
    ) -> Response:
        """Retorna componentes curriculares do funcionário.

        Args:
            _request: Requisição HTTP recebida.
            login: Login/RF do funcionário.
            id_perfil: Identificador do perfil.

        Returns:
            Resposta HTTP com os componentes ou status 204.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_funcionario(
            login=login,
            id_perfil=id_perfil,
        )
        if data == []:
            return Response(status=204)
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesTurmaFuncionarioViewSet(APIView):
    """Lista componentes do funcionário em uma turma."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes por turma, funcionário e perfil",
        description=(
            "Retorna os componentes curriculares atribuídos ao funcionário "
            "na turma informada. Permite controlar o agrupamento dos "
            "componentes e a aplicação das regras de disponibilização e de "
            "educação infantil."
        ),
        parameters=[
            OpenApiParameter(
                "agrupa_componente_curricular",
                OpenApiTypes.BOOL,
                OpenApiParameter.PATH,
                required=True,
                enum=[True, False],
                description=(
                    "Define se os componentes curriculares serão agrupados."
                ),
            ),
            OpenApiParameter(
                "checaMotivoDisponibilizacao",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=True,
                description=(
                    "Verifica o motivo de disponibilização da atribuição."
                ),
            ),
            OpenApiParameter(
                "consideraTurmaInfantil",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=True,
                description=(
                    "Aplica as regras específicas de turmas de educação "
                    "infantil."
                ),
            ),
        ],
        operation_id="componentes_turma_funcionario",
        responses={200: ComponenteCurricularSerializer(many=True), 204: None},
    )
    def get(
        self,
        request: Request,
        codigo_turma: str,
        login: str,
        id_perfil: str,
        agrupa_componente_curricular: str,
    ) -> Response:
        """Retorna componentes do funcionário em uma turma.

        Args:
            request: Requisição HTTP recebida.
            codigo_turma: Código da turma.
            login: Login/RF do funcionário.
            id_perfil: Identificador do perfil.
            agrupa_componente_curricular: Indicador de agrupamento.

        Returns:
            Resposta HTTP com os componentes ou status 204.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_turma_funcionario(
            codigo_turma=codigo_turma,
            login=login,
            id_perfil=id_perfil,
            agrupa_componente_curricular=(
                agrupa_componente_curricular.lower() == "true"
            ),
            checa_motivo_disponibilizacao=(
                request.query_params.get(
                    "checaMotivoDisponibilizacao", "true"
                ).lower()
                == "true"
            ),
            considera_turma_infantil=(
                request.query_params.get(
                    "consideraTurmaInfantil", "true"
                ).lower()
                == "true"
            ),
        )
        if data == []:
            return Response(status=204)
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesPlanejamentoViewSet(APIView):
    """Lista componentes de planejamento do funcionário em uma turma."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes de planejamento por turma e funcionário",
        description=(
            "Retorna os componentes curriculares disponíveis para o "
            "planejamento pedagógico do funcionário na turma. Componentes "
            "de regência são substituídos pelos respectivos componentes de "
            "planejamento quando aplicável."
        ),
        operation_id="componentes_planejamento_turma_funcionario",
        responses={200: ComponenteCurricularSerializer(many=True), 204: None},
    )
    def get(
        self,
        _request: Request,
        codigo_turma: str,
        login: str,
        id_perfil: str,
    ) -> Response:
        """Retorna componentes de planejamento.

        Args:
            _request: Requisição HTTP recebida.
            codigo_turma: Código da turma.
            login: Login/RF do funcionário.
            id_perfil: Identificador do perfil.

        Returns:
            Resposta HTTP com os componentes ou status 204.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_planejamento(
            codigo_turma=codigo_turma,
            login=login,
            id_perfil=id_perfil,
        )
        if data == []:
            return Response(status=204)
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesPorListaTurmasViewSet(APIView):
    """Lista componentes para planejamento por lista de turmas."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes para planejamento por lista de turmas",
        description=(
            "Retorna os componentes curriculares das turmas informadas. "
            "O parâmetro de planejamento controla a inclusão dos "
            "componentes associados ao planejamento de regência."
        ),
        parameters=[
            OpenApiParameter(
                "codigoTurmas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
                description="Lista de códigos das turmas consultadas.",
            ),
            OpenApiParameter(
                "adicionarComponentesPlanejamento",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                default=True,
                description=(
                    "Inclui os componentes de planejamento de regência."
                ),
            ),
        ],
        operation_id="componentes_lista_turmas",
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Retorna componentes das turmas informadas.

        Args:
            request: Requisição HTTP com os filtros.

        Returns:
            Resposta HTTP com os componentes encontrados.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_por_lista_turmas(
            codigos_turmas=request.query_params.getlist("codigoTurmas"),
            adicionar_componentes_planejamento=(
                request.query_params.get(
                    "adicionarComponentesPlanejamento", "true"
                ).lower()
                == "true"
            ),
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesTurmasRegularesViewSet(APIView):
    """Lista componentes de turmas regulares."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes curriculares de turmas regulares",
        description=(
            "Retorna os componentes curriculares das turmas regulares "
            "informadas, sem expandir componentes específicos de "
            "planejamento."
        ),
        parameters=[
            OpenApiParameter(
                "codigoTurmas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
                description="Lista de códigos das turmas regulares.",
            ),
        ],
        operation_id="componentes_turmas_regulares",
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Retorna componentes das turmas regulares informadas.

        Args:
            request: Requisição HTTP com os códigos das turmas.

        Returns:
            Resposta HTTP com os componentes encontrados.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_turmas_regulares(
            request.query_params.getlist("codigoTurmas")
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class DadosAulaTurmaViewSet(APIView):
    """Lista dados de aula por turma e componente curricular."""

    @extend_schema(
        tags=_TAG,
        summary="Dados de aula por turma e componente",
        description=(
            "Retorna os componentes curriculares de regência vinculados às "
            "turmas da unidade educacional no ano letivo informado. O "
            "semestre pode ser usado para modalidades com organização "
            "semestral."
        ),
        parameters=[
            OpenApiParameter(
                "ueCodigo",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                description="Código da unidade educacional.",
            ),
            OpenApiParameter(
                "anoLetivo",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
                description="Ano letivo da consulta.",
            ),
            OpenApiParameter(
                "componentesCurriculares",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
                style="form",
                explode=True,
                description=("Lista de códigos dos componentes curriculares."),
            ),
            OpenApiParameter(
                "semestre",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Semestre letivo, quando aplicável à modalidade."
                ),
            ),
        ],
        operation_id="dados_aula_turma",
        responses={200: DadosAulaTurmaSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Retorna dados de aula das turmas.

        Args:
            request: Requisição HTTP com os filtros.

        Returns:
            Resposta HTTP com os dados de aula encontrados.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se parâmetros ou resposta forem inválidos.
        """
        semestre = request.query_params.get("semestre")
        data = services.get_dados_aula_turma(
            ue_codigo=request.query_params.get("ueCodigo", ""),
            ano_letivo=int(request.query_params.get("anoLetivo", 0)),
            componentes_curriculares=_obter_lista_query(
                request,
                "componentesCurriculares",
            ),
            semestre=int(semestre) if semestre else None,
        )
        return Response(DadosAulaTurmaSerializer(data, many=True).data)


class ComponentesSemAtribuicaoViewSet(APIView):
    """Lista componentes sem atribuição em uma turma."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes da turma sem atribuição",
        description=(
            "Retorna as descrições dos componentes curriculares da turma "
            "que não possuem professor atribuído na data base informada. "
            "A data é recebida em ticks de DateTime do .NET."
        ),
        operation_id="componentes_turma_sem_atribuicao",
        responses={200: OpenApiTypes.STR},
    )
    def get(
        self,
        _request: Request,
        codigo_turma: str,
        data_base_tick: int,
    ) -> Response:
        """Retorna componentes sem professor atribuído.

        Args:
            _request: Requisição HTTP recebida.
            codigo_turma: Código da turma.
            data_base_tick: Data base representada em ticks do .NET.

        Returns:
            Resposta HTTP com as descrições dos componentes.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            OverflowError: Se os ticks excederem o limite do datetime.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_sem_atribuicao(
            codigo_turma=codigo_turma,
            data_base_tick=data_base_tick,
        )
        return Response(data)


class ComponentesTurmaAnoViewSet(APIView):
    """Lista componentes por anos escolares."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes por UE, modalidade, ano e anos escolares",
        description=(
            "Retorna componentes da grade de oferta filtrados pelos "
            "anos escolares informados via query param `anosEscolares`.\n\n"
            "**Modalidades:** 1=EI, 3=EJA, 4=CIEJA, 5=EF, 6=EM.\n\n"
        ),
        parameters=[
            OpenApiParameter(
                name="modalidade",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                enum=[1, 3, 4, 5, 6],
                description="Modalidades permitidas.",
            ),
            OpenApiParameter(
                "anosEscolares",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
                description='Séries escolares (ex.: `["1","2","3"]`).',
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(
        self, request: Request, ue_id: str, modalidade: int, ano_letivo: int
    ) -> Response:
        """Retorna componentes por UE, modalidade, ano e anos escolares.

        Args:
            request: Requisição HTTP com os anos escolares.
            ue_id: Código da unidade educacional.
            modalidade: Modalidade de ensino.
            ano_letivo: Ano letivo.

        Returns:
            Resposta HTTP com os componentes encontrados.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_componentes_ue_anos(
            ue_id=ue_id,
            modalidade=modalidade,
            ano_letivo=ano_letivo,
            anos_escolares=request.query_params.getlist("anosEscolares"),
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class GradeComponentesCurricularesViewSet(APIView):
    """Retorna a grade curricular por ano letivo."""

    @extend_schema(
        tags=_TAG,
        summary="Grade curricular por ano letivo",
        description=(
            "Retorna todos os componentes da grade curricular para o "
            "ano letivo, agrupados por série e modalidade. "
            "Inclui todas as modalidades: "
            "1=EI, 3=EJA, 4=CIEJA, 5=EF, 6=EM.\n\n"
        ),
        responses={200: GradeCurricularSerializer(many=True)},
    )
    def get(self, _request: Request, ano_letivo: int) -> Response:
        """Retorna a grade curricular por ano letivo.

        Args:
            _request: Requisição HTTP recebida.
            ano_letivo: Ano letivo.

        Returns:
            Resposta HTTP com a grade curricular.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_grade_curricular(ano_letivo)
        return Response(GradeCurricularSerializer(data, many=True).data)


class AgrupamentosCorrelacionadosViewSet(APIView):
    """Lista agrupamentos de Território do Saber correlacionados."""

    @extend_schema(
        tags=_TAG,
        summary="Agrupamentos correlacionados por cod_agrupamento",
        description=(
            "Retorna os agrupamentos de Território do Saber correlacionados "
            "ao `cod_agrupamento` informado. A data base é recebida em "
            "ticks de DateTime do .NET via query `dataBaseTick`."
        ),
        operation_id="agrupamentos_correlacionados",
        parameters=[
            OpenApiParameter(
                "dataBaseTick",
                OpenApiTypes.INT64,
                OpenApiParameter.QUERY,
                required=False,
                description="Data base em ticks do .NET.",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(self, request: Request, codigo_componente: int) -> Response:
        """Retorna agrupamentos correlacionados por `cod_agrupamento`.

        Args:
            request: Requisição HTTP recebida.
            codigo_componente: `cod_agrupamento` de origem.

        Returns:
            Resposta HTTP com os agrupamentos correlacionados.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            OverflowError: Se os ticks excederem o limite do datetime.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        data = services.get_agrupamentos_correlacionados(
            codigo_componente=codigo_componente,
            data_base_tick=_obter_data_base_tick(request),
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class AgrupamentosCorrelacionadosLoteViewSet(APIView):
    """Lista agrupamentos de Território do Saber correlacionados em lote."""

    @extend_schema(
        tags=_TAG,
        summary="Agrupamentos correlacionados em lote",
        description=(
            "Retorna os agrupamentos de Território do Saber correlacionados "
            "aos `cod_agrupamento` informados no corpo. A data base é "
            "recebida em ticks de DateTime do .NET via query `dataBaseTick`."
        ),
        operation_id="agrupamentos_correlacionados_lote",
        request={"application/json": _IDS_REQUEST_SCHEMA},
        parameters=[
            OpenApiParameter(
                "dataBaseTick",
                OpenApiTypes.INT64,
                OpenApiParameter.QUERY,
                required=False,
                description="Data base em ticks do .NET.",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        """Retorna agrupamentos correlacionados em lote.

        Args:
            request: Requisição HTTP com a lista de `cod_agrupamento` no corpo.

        Returns:
            Resposta HTTP com os agrupamentos correlacionados.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            OverflowError: Se os ticks excederem o limite do datetime.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        serializer = CodigoComponenteListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data:
            return Response([])

        data = services.post_agrupamentos_correlacionados(
            ids=serializer.validated_data,
            data_base_tick=_obter_data_base_tick(request),
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class AgrupamentosTerritorioViewSet(APIView):
    """Lista agrupamentos de Território do Saber por IDs."""

    @extend_schema(
        tags=_TAG,
        summary="Agrupamentos de Território do Saber por cod_agrupamento",
        description=(
            "Retorna os agrupamentos de Território do Saber correspondentes "
            "aos `cod_agrupamento` informados no corpo da requisição."
        ),
        operation_id="agrupamentos_territorio",
        request={"application/json": _IDS_REQUEST_SCHEMA},
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        """Retorna agrupamentos de Território do Saber por `cod_agrupamento`.

        Args:
            request: Requisição HTTP com a lista de `cod_agrupamento` no corpo.

        Returns:
            Resposta HTTP com os agrupamentos de Território do Saber.

        Raises:
            httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
            ValueError: Se a resposta do serviço não for JSON válido.
        """
        serializer = CodigoComponenteListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data:
            return Response([])

        data = services.post_agrupamentos_territorio(
            ids=serializer.validated_data,
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)
