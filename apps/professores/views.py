"""Views do domínio de professores."""

from typing import Any, NamedTuple, cast

import httpx
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.parsers import JSONParser
from rest_framework.request import Request

from apps.core.datetime import validar_data_str, validar_data_tick
from apps.core.responses import (
    Response,
    api_error_response_status_livre,
    detail_response,
)
from apps.core.views import DomainAPIView
from apps.professores import services
from apps.professores.serializers import (
    BuscarFuncionariosPorUeSerializer,
    BuscarProfessorTitularPorDisciplinaSerializer,
    BuscarTurmasElegiveisSerializer,
    DisciplinaTurmaAgrupamentoSerializer,
    DisciplinaTurmaAtribuidaSerializer,
    FuncionarioCargoSerializer,
    FuncionarioDadosSigpaeSerializer,
    FuncionarioEscolaSerializer,
    FuncionarioExternoSerializer,
    FuncionarioFuncaoAtividadeSerializer,
    FuncionarioFuncaoAtividadeUeSerializer,
    FuncionarioFuncaoExternaSerializer,
    FuncionarioLoginSerializer,
    FuncionarioSgpLegadoSerializer,
    FuncionarioUeLegadoSerializer,
    FuncionarioUnidadeLegadoSerializer,
    ListaStringSerializer,
    NomeServidorSerializer,
    ProfessorAtribuicaoPeriodoPathSerializer,
    ProfessorAtribuicaoTurmaDisciplinaSerializer,
    ProfessorAutoCompleteSerializer,
    ProfessorBuscarPorRfSerializer,
    ProfessoresTitularesParametrosSerializer,
    ProfessorRecorrenciaDataSerializer,
    ProfessorStatusAtribuicaoSerializer,
    ProfessorTurmaAtribuidaSimplificadaSerializer,
    ProfessorTurmaSerializer,
    SupervisorLegadoSerializer,
    TurmaAtribuidaProfessorSerializer,
    TurmasIdsSerializer,
    VerificarAtribuicaoDisciplinaQuerySerializer,
)

_TAG_ACESSOS = ["Acessos"]
_TAG_DRE = ["DiretoriaRegionalEducacao"]
_TAG_ESCOLA = ["Escola"]
_TAG_FUNCIONARIO = ["Funcionario"]
_TAG_PROFESSOR = ["Professor"]

_MSG_CODIGO_RF_OBRIGATORIO = "É necessário informar o codigoRF."
_MSG_CODIGO_UE_OBRIGATORIO = "É necessário informar o codigoUE."
_MSG_CODIGO_FUNCAO_EXTERNA_OBRIGATORIO = (
    "É necessário informar o codigoFuncaoExterna."
)
_MSG_CODIGO_FUNCAO_ATIVIDADE_OBRIGATORIO = (
    "É necessário informar o codigoFuncaoAtividade."
)
_MSG_REGISTRO_FUNCIONAL_OBRIGATORIO = (
    "É necessário informar o registro funcional."
)
_MSG_PERFIL_OBRIGATORIO = "É necessário informar o perfil."
_MSG_DRE_ID_OBRIGATORIO = "É necessário informar o dreId."
_MSG_UE_ID_OBRIGATORIO = "É necessário informar o ueId."
_MSG_NOME_OBRIGATORIO = "É necessário informar o nome."
_TAMANHO_MINIMO_NOME = 2
_MSG_RESPOSTA_INVALIDA_API = "Resposta inválida da API de professores."
_DOMINIO_PROFESSORES = "professores"
_CAMPOS_TURMA = {
    "codigo_turma",
    "data_disponibilizacao_aulas",
    "data_atribuicao_aula",
}
_MSG_TURMAS_NAO_ENCONTRADAS = "Não foram encontradas turmas atribuídas."
_MSG_LISTA_SUPERVISORES_OBRIGATORIA = (
    "A lista de códigos de supervisores é obrigatória."
)
_MSG_SUPERVISORES_NAO_ENCONTRADOS = "Não foram encontrados supervisores."
_MSG_LISTA_LOGINS_OBRIGATORIA = "É necessario informar uma lista de Logins"
_MSG_CODIGO_TURMA_OBRIGATORIO = "É necessário informar o codigoTurma."
_MSG_DATA_VALIDA = "Deve ser informada uma data valida."
_MSG_DISCIPLINA_ID_OBRIGATORIO = "É necessário informar o disciplinaId."
_MSG_DATAS_TICKS_OBRIGATORIAS = "É necessário informar as datas em ticks!"

# Parâmetros temporários usados enquanto a identidade não informa
# a abrangência.
_PARAM_ABRANGENCIA_TEMPORARIO = OpenApiParameter(
    "abrangencia",
    OpenApiTypes.INT,
    OpenApiParameter.QUERY,
    required=False,
    enum=[1, 2, 3, 4, 5, 6],
    description=(
        "TEMPORÁRIO (removido após a integração com identidade). "
        "Tipo de abrangência: 1=UE, 2=Professor, 3=UeTurmasDisciplinas, "
        "4=Dre, 5=DreEscolasAtribuidas, 6=SME."
    ),
)
_PARAM_CARGOS_TEMPORARIO = OpenApiParameter(
    "cargos",
    OpenApiTypes.INT,
    OpenApiParameter.QUERY,
    required=False,
    many=True,
    description=(
        "TEMPORÁRIO (removido após a integração com identidade). "
        "Cargos do perfil (viriam do CoreSSO); filtram as abrangências "
        "de vínculo com UE/DRE."
    ),
)
_PARAM_FUNCOES_TEMPORARIO = OpenApiParameter(
    "funcoesId",
    OpenApiTypes.INT,
    OpenApiParameter.QUERY,
    required=False,
    many=True,
    description=(
        "TEMPORÁRIO (removido após a integração com identidade). "
        "Funções de atividade do perfil (viriam do CoreSSO); compõem o "
        "bloco de abrangência retornado."
    ),
)
_PARAM_GRUPO_TEMPORARIO = OpenApiParameter(
    "grupo",
    OpenApiTypes.INT,
    OpenApiParameter.QUERY,
    required=False,
    description=(
        "TEMPORÁRIO (removido após a integração com identidade). "
        "Grupo/perfil (viria do CoreSSO); compõe o bloco de abrangência "
        "retornado."
    ),
)
_PARAM_DRE_CODIGO_TEMPORARIO = OpenApiParameter(
    "dreCodigo",
    OpenApiTypes.STR,
    OpenApiParameter.QUERY,
    required=False,
    description=(
        "TEMPORÁRIO (removido após a integração com identidade). "
        "Código da DRE atribuída (viria do CoreSSO); usado na abrangência "
        "de turmas por DRE."
    ),
)
_PARAM_EH_PERFIL_MANUAL_TEMPORARIO = OpenApiParameter(
    "ehPerfilManual",
    OpenApiTypes.BOOL,
    OpenApiParameter.QUERY,
    required=False,
    description=(
        "TEMPORÁRIO (removido após a integração com identidade). "
        "Marca de perfil manual (viria do CoreSSO); compõe o bloco de "
        "abrangência retornado."
    ),
)
_PARAM_CODIGO_DRE_LEGADO = OpenApiParameter(
    "CodigoDre",
    OpenApiTypes.STR,
    OpenApiParameter.QUERY,
    required=False,
    description=(
        "Código da DRE usado na consulta por perfil quando informado."
    ),
)
_PARAM_CODIGO_UE_LEGADO = OpenApiParameter(
    "CodigoUe",
    OpenApiTypes.STR,
    OpenApiParameter.QUERY,
    required=False,
    description="Código da unidade educacional usado no filtro.",
)
_PARAM_CODIGO_RF_LEGADO = OpenApiParameter(
    "CodigoRf",
    OpenApiTypes.STR,
    OpenApiParameter.QUERY,
    required=False,
    description="Registro funcional usado na consulta por perfil.",
)
_PARAM_NOME_SERVIDOR_LEGADO = OpenApiParameter(
    "NomeServidor",
    OpenApiTypes.STR,
    OpenApiParameter.QUERY,
    required=False,
    description="Nome do servidor usado no filtro.",
)
# Planejamento: os branches curto-circuitam, então só a abrangência é útil.
_PARAMS_ABRANGENCIA_TEMPORARIOS = [_PARAM_ABRANGENCIA_TEMPORARIO]
# Disciplinas: o branch de vínculo com UE/DRE filtra por cargos.
_PARAMS_DISCIPLINAS_TEMPORARIOS = [
    _PARAM_ABRANGENCIA_TEMPORARIO,
    _PARAM_CARGOS_TEMPORARIO,
]
# Turmas: switch completo por abrangência, incluindo o branch por DRE.
_PARAMS_TURMAS_TEMPORARIOS = [
    _PARAM_ABRANGENCIA_TEMPORARIO,
    _PARAM_CARGOS_TEMPORARIO,
    _PARAM_FUNCOES_TEMPORARIO,
    _PARAM_GRUPO_TEMPORARIO,
    _PARAM_DRE_CODIGO_TEMPORARIO,
    _PARAM_EH_PERFIL_MANUAL_TEMPORARIO,
]
_PARAMS_FUNCIONARIOS_PERFIL = [
    _PARAM_CODIGO_DRE_LEGADO,
    _PARAM_CODIGO_UE_LEGADO,
    _PARAM_CODIGO_RF_LEGADO,
    _PARAM_NOME_SERVIDOR_LEGADO,
]


class _AbrangenciaTemporaria(NamedTuple):
    """Parâmetros temporários que substituem os dados do CoreSSO."""

    abrangencia: int | None
    cargos: list[int] | None
    funcoes: list[int] | None
    grupo: int | None
    dre_codigo: str | None
    eh_perfil_manual: bool


def _inteiro_param(request: Request, nome: str) -> int | None:
    """Lê um parâmetro inteiro único da requisição."""
    bruto = request.query_params.get(nome)
    return int(bruto) if bruto and bruto.isdigit() else None


def _inteiros_param(request: Request, nome: str) -> list[int] | None:
    """Lê um parâmetro inteiro repetido da requisição."""
    valores = [
        item
        for item in request.query_params.getlist(nome)
        if item.strip().isdigit()
    ]
    return [int(item) for item in valores] or None


class ProfessoresAPIView(DomainAPIView):
    """APIView base que padroniza falhas de comunicação com professores."""

    api_domain = _DOMINIO_PROFESSORES


class JsonPatchParser(JSONParser):
    """Processa payload JSON Patch como JSON."""

    media_type = "application/json-patch+json"


def _abrangencia_temporaria(request: Request) -> _AbrangenciaTemporaria:
    """Lê os parâmetros temporários que substituem os dados do CoreSSO."""
    return _AbrangenciaTemporaria(
        abrangencia=_inteiro_param(request, "abrangencia"),
        cargos=_inteiros_param(request, "cargos"),
        funcoes=_inteiros_param(request, "funcoesId"),
        grupo=_inteiro_param(request, "grupo"),
        dre_codigo=request.query_params.get("dreCodigo") or None,
        eh_perfil_manual=(
            request.query_params.get("ehPerfilManual", "").lower() == "true"
        ),
    )


def _query_params(
    request: Request,
    lista: set[str],
    simples: set[str],
) -> dict[str, str | list[str]]:
    """Coleta parâmetros de consulta informados na requisição.

    Args:
        request: Requisição com os parâmetros de consulta.
        lista: Nomes de parâmetros que aceitam múltiplos valores.
        simples: Nomes de parâmetros com valor único.

    Returns:
        Parâmetros presentes, como lista ou valor único conforme o nome.
    """
    params: dict[str, str | list[str]] = {}
    for nome in lista:
        valores = request.query_params.getlist(nome)
        if valores:
            params[nome] = valores
    for nome in simples:
        valor = request.query_params.get(nome)
        if valor is not None:
            params[nome] = valor
    return params


def _parse_bool_param(value: str | None) -> bool | None:
    """Retorna o booleano correspondente ao parâmetro textual.

    Args:
        value: Valor textual recebido na consulta.

    Returns:
        Booleano correspondente, ou ``None`` quando o valor não é reconhecido.
    """
    if value is None:
        return None
    normalized = value.lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None


def _is_lista_turmas(data: object) -> bool:
    """Verifica se os dados representam uma lista de turmas.

    Args:
        data: Conteúdo retornado pela consulta.

    Returns:
        ``True`` quando todos os itens têm os campos de turma esperados.
    """
    return isinstance(data, list) and all(
        isinstance(item, dict) and item.keys() >= _CAMPOS_TURMA
        for item in data
    )


def _is_lista_dicionarios(data: object) -> bool:
    """Verifica se os dados são uma lista de dicionários.

    Args:
        data: Conteúdo retornado pela consulta.

    Returns:
        ``True`` quando os dados são uma lista composta só de dicionários.
    """
    return isinstance(data, list) and all(
        isinstance(item, dict) for item in data
    )


class ProfessorView(ProfessoresAPIView):
    """Retorna o nome do professor pelo RF."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Retorna o nome do professor correspondente ao RF informado."
        ),
        responses={200: OpenApiTypes.STR, 204: None},
    )
    def get(self, _request: Request, rf_professor: str) -> Response:
        """Retorna o nome do professor pelo código RF.

        Args:
            rf_professor: Registro funcional usado na consulta.

        Returns:
            Nome do professor, ou ausência de conteúdo quando não encontrado.
        """
        if not rf_professor.strip():
            return detail_response("Codigo RF e obrigatorio.")
        data = services.get_professor(rf_professor)
        if data is None:
            return Response(status=204)
        return Response(data)


class ValidadeProfessorView(ProfessoresAPIView):
    """Retorna indicação de validade do professor."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=("Retorna booleano indicando se o professor é válido."),
        responses={200: OpenApiTypes.BOOL},
    )
    def get(self, _request: Request, codigo_rf: str) -> Response:
        """Retorna indicação de validade do professor.

        Args:
            codigo_rf: RF usado na consulta de validade.

        Returns:
            Indicador booleano de validade do professor.
        """
        if not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        data = services.get_validade_professor(codigo_rf)
        return Response(data)


class ProfessorVerificarAtribuicaoDataView(ProfessoresAPIView):
    """Verifica a atribuição do professor em uma data."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Verifica se o professor possui atribuição de turma em uma "
            "data específica."
        ),
        responses={200: OpenApiTypes.BOOL, 400: OpenApiTypes.STR},
        parameters=[
            OpenApiParameter(
                "dataConsulta",
                OpenApiTypes.DATE,
                OpenApiParameter.QUERY,
                required=True,
                description=("Data a ser verificada no formato YYYY-MM-DD."),
            )
        ],
    )
    def get(
        self,
        _request: Request,
        codigo_rf: str,
        codigo_turma: str,
    ) -> Response:
        """Verifica a atribuição do professor em uma data.

        Args:
            codigo_rf: RF do professor.
            codigo_turma: Código da turma.

        Returns:
            Indicador booleano de atribuição do professor na turma.
        """
        if not codigo_rf.strip():
            return Response(_MSG_CODIGO_RF_OBRIGATORIO, status=400)
        if not codigo_turma.strip():
            return Response(_MSG_CODIGO_TURMA_OBRIGATORIO, status=400)

        data: str | None = _request.query_params.get("dataConsulta")
        if not data or validar_data_str(data) is False:
            return Response(_MSG_DATA_VALIDA, status=400)

        resposta = services.verificar_atribuicao_professor_turma(
            codigo_rf, codigo_turma, data
        )
        return Response(resposta)


class ProfessorVerificarAtribuicaoPeriodoView(ProfessoresAPIView):
    """Verifica a atribuição do professor em um período."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Verifica se o professor possui atribuição na turma e "
            "componente curricular durante o período informado."
        ),
        responses={200: OpenApiTypes.BOOL, 400: OpenApiTypes.OBJECT},
    )
    def post(
        self,
        _request: Request,
        codigo_rf: str,
        codigo_turma: str,
        componente_curricular_id: str,
        data_inicio_periodo: str,
        data_fim_periodo: str,
    ) -> Response:
        """Retorna se existe atribuição sobreposta ao período.

        Args:
            codigo_rf: RF do professor.
            codigo_turma: Código da turma.
            componente_curricular_id: ID do componente curricular.
            data_inicio_periodo: Início do período em formato ISO 8601.
            data_fim_periodo: Fim do período em formato ISO 8601.

        Returns:
            Indicador booleano de atribuição no período.
        """
        serializer = ProfessorAtribuicaoPeriodoPathSerializer(
            data={
                "codigo_rf": codigo_rf,
                "codigo_turma": codigo_turma,
                "componente_curricular_id": componente_curricular_id,
                "data_inicio_periodo": data_inicio_periodo,
                "data_fim_periodo": data_fim_periodo,
            }
        )
        if not serializer.is_valid():
            return detail_response("Parâmetros do período são inválidos.")

        dados = serializer.validated_data
        resposta = services.verificar_atribuicao_periodo(
            dados["codigo_rf"],
            dados["codigo_turma"],
            dados["componente_curricular_id"],
            dados["data_inicio_periodo"].isoformat(),
            dados["data_fim_periodo"].isoformat(),
        )
        return Response(resposta)


class ProfessoresTitularesPorTurmaView(ProfessoresAPIView):
    """Busca professores titulares de uma turma."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Busca professores titulares da turma, com opção de agrupar "
            "componentes curriculares."
        ),
        parameters=[
            OpenApiParameter(
                "realiza_agrupamento",
                OpenApiTypes.BOOL,
                OpenApiParameter.PATH,
                required=True,
                description=(
                    "Indica se os componentes curriculares devem ser "
                    "agrupados."
                ),
            ),
            OpenApiParameter(
                "codigoRF",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                "dataReferencia",
                OpenApiTypes.DATETIME,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={
            200: BuscarProfessorTitularPorDisciplinaSerializer(many=True),
            204: None,
            400: OpenApiTypes.OBJECT,
        },
    )
    def get(
        self,
        request: Request,
        codigo_turma: str,
        realiza_agrupamento: bool,
    ) -> Response:
        """Retorna professores titulares da turma.

        Args:
            request: Requisição HTTP com os filtros opcionais.
            codigo_turma: Código da turma consultada.
            realiza_agrupamento: Indicador de agrupamento dos componentes.

        Returns:
            Professores encontrados, ausência de conteúdo ou erro de
            validação.
        """
        serializer = ProfessoresTitularesParametrosSerializer(
            data={
                "codigo_turma": codigo_turma,
                "codigoRF": request.query_params.get("codigoRF", ""),
                "dataReferencia": request.query_params.get("dataReferencia"),
                "realiza_agrupamento": realiza_agrupamento,
            }
        )
        if not serializer.is_valid():
            return detail_response(
                "Código RF e Código de Turma, são obrigatórios."
            )

        dados = serializer.validated_data
        professores = services.buscar_professores_titulares_por_turma(
            dados["codigo_turma"],
            dados["codigo_rf"],
            dados["data_referencia"],
            dados["realiza_agrupamento"],
        )
        if not professores:
            return Response(status=204)
        resposta = BuscarProfessorTitularPorDisciplinaSerializer(
            professores,
            many=True,
        )
        return Response(resposta.data)


class ProfessorStatusAtribuicaoView(ProfessoresAPIView):
    """Obtém o status da atribuição do professor em uma turma."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Obtém o status da atribuição do professor em uma turma "
            "específica."
        ),
        responses={200: ProfessorStatusAtribuicaoSerializer},
    )
    def get(
        self,
        _request: Request,
        codigo_rf: str,
        codigo_turma: str,
    ) -> Response:
        """Obtém o status da atribuição do professor em uma turma.

        Args:
            codigo_rf: RF do professor.
            codigo_turma: Código da turma.

        Returns:
            Status da atribuição do professor na turma.
        """
        if not codigo_rf.strip():
            return Response(_MSG_CODIGO_RF_OBRIGATORIO, status=400)
        if not codigo_turma.strip():
            return Response(_MSG_CODIGO_TURMA_OBRIGATORIO, status=400)

        resposta = services.get_status_atribuicao_professor_turma(
            codigo_rf, codigo_turma
        )
        return Response(resposta)


class ProfessorVerificarAtribuicaoDataTickView(ProfessoresAPIView):
    """Verifica a atribuição do professor em uma data por tick."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Verifica se o professor possui atribuição de turma e disciplina "
            "em uma data específica, informada como tick."
        ),
        responses={200: OpenApiTypes.BOOL, 400: OpenApiTypes.STR},
        parameters=[
            OpenApiParameter(
                "dataConsultaTick",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
                description=(
                    "Data a ser verificada no formato de tick (milissegundos "
                    "desde 1970-01-01)."
                ),
            )
        ],
    )
    def get(
        self,
        _request: Request,
        codigo_rf: str,
        codigo_turma: str,
        disciplina_id: str,
    ) -> Response:
        """Verifica a atribuição do professor em uma data por tick.

        Args:
            codigo_rf: RF do professor.
            codigo_turma: Código da turma.
            disciplina_id: ID da disciplina.
            dataConsultaTick: Data a ser verificada no formato de tick.

        Returns:
            Indicador booleano de atribuição do professor na turma
            e disciplina.
        """
        if not codigo_rf.strip():
            return Response(_MSG_CODIGO_RF_OBRIGATORIO, status=400)
        if not codigo_turma.strip():
            return Response(_MSG_CODIGO_TURMA_OBRIGATORIO, status=400)
        if not disciplina_id.strip():
            return Response(_MSG_DISCIPLINA_ID_OBRIGATORIO, status=400)

        data_consulta_tick: str | None = _request.query_params.get(
            "dataConsultaTick"
        )
        if (
            not data_consulta_tick
            or validar_data_tick(data_consulta_tick) is False
        ):
            return Response(_MSG_DATA_VALIDA, status=400)

        resposta = services.verificar_atribuicao_professor_turma_disciplina(
            codigo_rf, codigo_turma, disciplina_id, data_consulta_tick
        )
        return Response(resposta)


class ProfessorAtribuicaoTurmaDisciplinaView(ProfessoresAPIView):
    """Obtém a atribuições de uma turma e disciplina."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Obtém a atribuições de uma turma e disciplina, filtrando por "
            "datas informadas como ticks."
        ),
        responses={
            200: ProfessorAtribuicaoTurmaDisciplinaSerializer(many=True),
            400: OpenApiTypes.STR,
        },
        parameters=[
            OpenApiParameter(
                "dataTicks",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
                description=(
                    "Datas a serem verificadas no formato de tick "
                    "(milissegundos"
                    "desde 1970-01-01)."
                ),
            )
        ],
    )
    def get(
        self,
        _request: Request,
        codigo_turma: str,
        disciplina_id: str,
    ) -> Response:
        """Obtém a atribuições de uma turma e disciplina.

        Args:
            codigo_turma: Código da turma.
            disciplina_id: ID da disciplina.
            dataTicks: Data a ser verificada no formato de tick.

        Returns:
            Atribuições da turma e disciplina.
        """
        if not codigo_turma.strip():
            return Response(_MSG_CODIGO_TURMA_OBRIGATORIO, status=400)
        if not disciplina_id.strip():
            return Response(_MSG_DISCIPLINA_ID_OBRIGATORIO, status=400)

        data: str | None = _request.query_params.get("dataTicks")
        if not data or validar_data_tick(data) is False:
            return Response(_MSG_DATA_VALIDA, status=400)

        resposta = services.get_atribuicoes_turma_disciplina(
            codigo_turma, disciplina_id, data
        )
        return Response(resposta)


class ProfessorVerificarRecorrenciaDatasView(ProfessoresAPIView):
    """Verifica datas de recorrência de uma atribuição docente."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Verifica se as datas recorrentes de uma atribuição podem "
            "ser persistidas."
        ),
        responses={
            200: ProfessorRecorrenciaDataSerializer(many=True),
            400: OpenApiTypes.STR,
        },
        parameters=[
            OpenApiParameter(
                "datasTicks",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
                description=(
                    "Datas recorrentes em ticks de DateTime do .NET. O "
                    "parâmetro pode ser repetido."
                ),
            )
        ],
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        codigo_turma: str,
        disciplina_id: str,
    ) -> Response:
        """Verifica as datas de recorrência informadas.

        Args:
            request: Requisição HTTP com as datas em ticks.
            codigo_rf: RF do professor.
            codigo_turma: Código da turma.
            disciplina_id: ID da disciplina.
            dataTicks: Datas recorrentes em ticks de DateTime do .NET.

        Returns:
            Permissões de persistência para cada data informada.
        """
        datas_ticks = request.query_params.getlist("datasTicks")
        if not datas_ticks or not all(map(validar_data_tick, datas_ticks)):
            return Response(_MSG_DATAS_TICKS_OBRIGATORIAS, status=400)

        resultado = services.verificar_recorrencia_datas(
            codigo_rf,
            codigo_turma,
            disciplina_id,
            datas_ticks,
        )
        serializer = ProfessorRecorrenciaDataSerializer(resultado, many=True)
        return Response(serializer.data)  # type: ignore[has-type]


class ProfessorVerificarAtribuicaoTurmaDisciplinaDataView(ProfessoresAPIView):
    """Verifica a atribuição do professor em uma turma e disciplina."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Verifica se o professor possui atribuição de turma e disciplina "
            "em uma data específica."
        ),
        responses={200: OpenApiTypes.BOOL, 400: OpenApiTypes.STR},
        parameters=[
            OpenApiParameter(
                "dataConsulta",
                OpenApiTypes.DATE,
                OpenApiParameter.QUERY,
                required=True,
                description=("Data a ser verificada no formato YYYY-MM-DD."),
            ),
            OpenApiParameter(
                "territorioSaber",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Indica se a verificação é para o território saber."
                ),
                default=False,
            ),
        ],
    )
    def get(
        self,
        _request: Request,
        codigo_rf: str,
        codigo_turma: str,
        disciplina_id: str,
    ) -> Response:
        """Verifica a atribuição do professor em uma turma e disciplina.

        Args:
            codigo_rf: RF do professor.
            codigo_turma: Código da turma.
            disciplina_id: ID da disciplina.
            dataConsulta: Data a ser verificada.
            territorioSaber: Indica se a verificação é para o território saber.

        Returns:
            Indicador booleano de atribuição do professor na turma
            e disciplina.
        """
        if not codigo_rf.strip():
            return Response(_MSG_CODIGO_RF_OBRIGATORIO, status=400)
        if not codigo_turma.strip():
            return Response(_MSG_CODIGO_TURMA_OBRIGATORIO, status=400)
        if not disciplina_id.strip():
            return Response(_MSG_DISCIPLINA_ID_OBRIGATORIO, status=400)

        data_consulta: str | None = _request.query_params.get("dataConsulta")
        if not data_consulta or validar_data_str(data_consulta) is False:
            return Response(_MSG_DATA_VALIDA, status=400)

        query_serializer = VerificarAtribuicaoDisciplinaQuerySerializer(
            data=_request.query_params
        )
        query_serializer.is_valid(raise_exception=True)
        territorio_saber: bool = query_serializer.validated_data[
            "territorioSaber"
        ]

        resposta = services.verificar_atribuicao_disciplina_territorio_saber(
            codigo_rf,
            codigo_turma,
            disciplina_id,
            data_consulta,
            territorio_saber,
        )
        return Response(resposta)


class FuncionarioAtivoView(ProfessoresAPIView):
    """Retorna indicação de atividade do funcionário."""

    @extend_schema(
        tags=_TAG_ACESSOS,
        description=(
            "Retorna booleano indicando se o funcionário está ativo."
        ),
        responses={200: OpenApiTypes.BOOL},
    )
    def get(self, _request: Request, registro_funcional: str) -> Response:
        """Retorna indicação de atividade do funcionário.

        Args:
            registro_funcional: Registro funcional usado na consulta.

        Returns:
            Indicador booleano de funcionário ativo.
        """
        if not registro_funcional.strip():
            return detail_response(_MSG_REGISTRO_FUNCIONAL_OBRIGATORIO)
        data = services.get_funcionario_ativo(registro_funcional)
        return Response(data)


class NomeServidorView(ProfessoresAPIView):
    """Retorna nome e CPF do servidor."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna nome e CPF do servidor."),
        responses={200: NomeServidorSerializer, 204: None},
    )
    def get(self, _request: Request, registro_funcional: str) -> Response:
        """Retorna nome e CPF do servidor.

        Args:
            registro_funcional: Registro funcional usado na consulta.

        Returns:
            Dados de identificação do servidor, ou ausência de conteúdo.
        """
        data = services.get_nome_servidor(registro_funcional)
        if data is None:
            return Response(status=204)
        return Response(NomeServidorSerializer(data).data)


class NomeUsuarioEolView(ProfessoresAPIView):
    """Retorna nome de usuário EOL do funcionário."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna o nome de usuário EOL do funcionário."),
        responses={200: OpenApiTypes.STR, 204: None},
    )
    def get(self, _request: Request, registro_funcional: str) -> Response:
        """Retorna nome de usuário EOL do funcionário.

        Args:
            registro_funcional: Registro funcional usado na consulta.

        Returns:
            Nome de usuário EOL, ou ausência de conteúdo quando não encontrado.
        """
        if not registro_funcional.strip():
            return detail_response(_MSG_REGISTRO_FUNCIONAL_OBRIGATORIO)
        data = services.get_nome_usuario_eol(registro_funcional)
        if data is None:
            return Response(status=204)
        return Response(data)


class FuncionarioTurmaDisciplinasView(ProfessoresAPIView):
    """Retorna disciplinas da turma."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna disciplinas vinculadas à turma."),
        responses={200: DisciplinaTurmaAgrupamentoSerializer(many=True)},
    )
    def get(self, _request: Request, codigo_turma: str) -> Response:
        """Retorna disciplinas da turma.

        Args:
            codigo_turma: Código da turma usada na consulta.

        Returns:
            Disciplinas da turma, ou ausência de conteúdo.
        """
        if not codigo_turma.strip():
            return detail_response(_MSG_CODIGO_TURMA_OBRIGATORIO)
        data = services.get_disciplinas_turma(codigo_turma)
        if data == []:
            return Response(status=204)
        return Response(data)


class FuncionarioPerfilTurmaDisciplinasView(ProfessoresAPIView):
    """Retorna disciplinas do funcionário na turma."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna disciplinas do funcionário na turma."),
        parameters=_PARAMS_DISCIPLINAS_TEMPORARIOS,
        responses={200: DisciplinaTurmaAtribuidaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        login: str,
        id_perfil: str,
        codigo_turma: str,
    ) -> Response:
        """Retorna disciplinas do funcionário na turma.

        Args:
            request: Requisição com os parâmetros temporários de abrangência.
            login: Login/RF usado na consulta.
            id_perfil: Perfil usado na consulta.
            codigo_turma: Código da turma usada na consulta.

        Returns:
            Disciplinas da turma, ou ausência de conteúdo.
        """
        response = _validar_disciplinas_funcionario(
            login,
            id_perfil,
            codigo_turma,
        )
        if response is not None:
            return response
        params = _abrangencia_temporaria(request)
        data = services.get_disciplinas_funcionario_turma(
            login,
            id_perfil,
            codigo_turma,
            abrangencia=params.abrangencia,
            cargos=params.cargos,
        )
        if data == []:
            return Response(status=204)
        return Response(data)


class FuncionarioPerfilTurmaDisciplinasPlanejamentoView(ProfessoresAPIView):
    """Retorna disciplinas de planejamento do funcionário na turma."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=(
            "Retorna disciplinas de planejamento do funcionário na turma."
        ),
        parameters=_PARAMS_ABRANGENCIA_TEMPORARIOS,
        responses={200: DisciplinaTurmaAtribuidaSerializer(many=True)},
    )
    def get(
        self,
        request: Request,
        login: str,
        id_perfil: str,
        codigo_turma: str,
    ) -> Response:
        """Retorna disciplinas de planejamento do funcionário na turma.

        Args:
            request: Requisição com os parâmetros temporários de abrangência.
            login: Login/RF usado na consulta.
            id_perfil: Perfil usado na consulta.
            codigo_turma: Código da turma usada na consulta.

        Returns:
            Disciplinas da turma, ou ausência de conteúdo.
        """
        response = _validar_disciplinas_funcionario(
            login,
            id_perfil,
            codigo_turma,
        )
        if response is not None:
            return response
        params = _abrangencia_temporaria(request)
        data = services.get_disciplinas_funcionario_turma(
            login,
            id_perfil,
            codigo_turma,
            planejamento=True,
            abrangencia=params.abrangencia,
        )
        if data == []:
            return Response(status=204)
        return Response(data)


def _validar_disciplinas_funcionario(
    login: str,
    id_perfil: str,
    codigo_turma: str,
) -> Response | None:
    """Valida parâmetros da consulta de disciplinas."""
    if not login.strip():
        return detail_response("É necessário informar o login.")
    if not id_perfil.strip():
        return detail_response("É necessário informar o idPerfil.")
    if not codigo_turma.strip():
        return detail_response(_MSG_CODIGO_TURMA_OBRIGATORIO)
    return None


class ProfessorBuscarPorRfView(ProfessoresAPIView):
    """Retorna dados resumidos de professor."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=("Retorna professor por RF e ano letivo."),
        parameters=[
            OpenApiParameter(
                "buscar_outros_cargos",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: ProfessorBuscarPorRfSerializer, 204: None},
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        ano_letivo: int,
    ) -> Response:
        """Retorna professor por RF e ano letivo.

        Args:
            request: Requisição com o filtro opcional de outros cargos.
            codigo_rf: RF usado na consulta.
            ano_letivo: Ano letivo de referência.

        Returns:
            Dados resumidos do professor, ou ausência de conteúdo.
        """
        if not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        buscar_outros_cargos_param = request.query_params.get(
            "buscar_outros_cargos"
        )
        buscar_outros_cargos = _parse_bool_param(buscar_outros_cargos_param)
        if (
            buscar_outros_cargos_param is not None
            and buscar_outros_cargos is None
        ):
            return detail_response("buscar_outros_cargos deve ser booleano.")
        data = services.get_professor_por_rf(
            codigo_rf,
            ano_letivo,
            buscar_outros_cargos,
        )
        if data is None:
            return Response(status=204)
        return Response(ProfessorBuscarPorRfSerializer(data).data)


class FuncionariosBuscarPorListaRfView(ProfessoresAPIView):
    """Retorna professores pelos RFs informados."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna professores pelos RFs informados."),
        request=ListaStringSerializer,
        responses={200: ProfessorBuscarPorRfSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        """Retorna professores pelos RFs informados.

        Args:
            request: Requisição com a lista de RFs no corpo.

        Returns:
            Professores encontrados, ou ausência de conteúdo.

        Raises:
            ValidationError: Quando a lista de RFs informada é inválida.
        """
        serializer = ListaStringSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = services.get_professores_por_lista_rf(serializer.validated_data)
        if data is None:
            return Response(status=204)
        return Response(ProfessorBuscarPorRfSerializer(data, many=True).data)


class FuncionarioExternoCPFView(ProfessoresAPIView):
    """Retorna funcionarios externos por CPF."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna funcionarios externos por CPF."),
        responses={
            200: FuncionarioExternoSerializer(many=True),
            204: None,
            502: dict,
        },
    )
    def get(self, _request: Request, cpf: str) -> Response:
        """Retorna funcionarios externos por CPF.

        Args:
            cpf: CPF usado na consulta.

        Returns:
            Funcionarios externos encontrados, ou ausencia de dados.
        """
        if not cpf.strip():
            return detail_response("E necessario informar o CPF.")
        try:
            data = services.get_funcionario_externo(cpf)
        except httpx.HTTPStatusError as exc:
            return api_error_response_status_livre(exc)
        if not data:
            return Response(status=204)
        if not _is_lista_dicionarios(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(FuncionarioExternoSerializer(data, many=True).data)


class FuncionariosBuscarPorListaLoginView(ProfessoresAPIView):
    """Retorna funcionarios pelos logins informados."""

    parser_classes = [JSONParser, JsonPatchParser]

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna funcionarios pelos logins informados."),
        request=ListaStringSerializer,
        responses={
            200: FuncionarioLoginSerializer(many=True),
            204: None,
            400: dict,
            502: dict,
        },
    )
    def post(self, request: Request) -> Response:
        """Retorna funcionarios pelos logins informados.

        Args:
            request: Requisicao com a lista de logins no corpo.

        Returns:
            Funcionarios encontrados, ou ausencia de dados.
        """
        if request.data == []:
            return Response(_MSG_LISTA_LOGINS_OBRIGATORIA, status=400)
        serializer = ListaStringSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            data = services.get_funcionarios_por_lista_login(
                serializer.validated_data
            )
        except httpx.HTTPStatusError as exc:
            return api_error_response_status_livre(exc)
        if data is None:
            return Response(status=204)
        if not _is_lista_dicionarios(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(FuncionarioLoginSerializer(data, many=True).data)


class FuncionariosUnidadeView(ProfessoresAPIView):
    """Retorna funcionarios por unidade e perfis."""

    parser_classes = [JSONParser, JsonPatchParser]

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna funcionarios por unidade e perfis."),
        request=ListaStringSerializer,
        responses={
            200: FuncionarioUnidadeLegadoSerializer(many=True),
            204: None,
            400: dict,
            404: str,
            502: dict,
        },
    )
    def post(self, request: Request, codigo_dre_ue: str) -> Response:
        """Retorna funcionarios por unidade e perfis.

        Args:
            request: Requisicao com a lista de perfis no corpo.
            codigo_dre_ue: Codigo da unidade ou DRE/UE usada na consulta.

        Returns:
            Funcionarios encontrados, ou ausencia de dados.
        """
        if not codigo_dre_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        serializer = ListaStringSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            data = services.get_funcionarios_unidade(
                codigo_dre_ue,
                serializer.validated_data,
            )
        except httpx.HTTPStatusError as exc:
            return api_error_response_status_livre(exc)
        if data is None:
            return Response(status=204)
        if not isinstance(data, list):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        if not data:
            return Response(
                "Nao foram encontrados funcionarios.",
                status=404,
            )
        if not _is_lista_dicionarios(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(
            FuncionarioUnidadeLegadoSerializer(data, many=True).data
        )


class FuncionariosAdminsSmeView(ProfessoresAPIView):
    """Retorna administradores SME pelos perfis informados."""

    parser_classes = [JSONParser, JsonPatchParser]

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna administradores SME pelos perfis informados."),
        request=ListaStringSerializer,
        responses={
            200: ListaStringSerializer,
            204: None,
            400: dict,
            502: dict,
        },
    )
    def post(self, request: Request) -> Response:
        """Retorna administradores SME pelos perfis informados.

        Args:
            request: Requisicao com a lista de perfis no corpo.

        Returns:
            Lista de RFs/logins dos administradores, ou ausencia de dados.
        """
        serializer = ListaStringSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            data = services.get_funcionarios_admins_sme(
                serializer.validated_data
            )
        except httpx.HTTPStatusError as exc:
            return api_error_response_status_livre(exc)
        if data is None:
            return Response(status=204)
        if not isinstance(data, list) or not all(
            isinstance(item, str) for item in data
        ):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(data)


class FuncionarioDadosSigpaeView(ProfessoresAPIView):
    """Retorna dados SIGPAE do funcionario."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna dados SIGPAE do funcionario."),
        responses={
            200: FuncionarioDadosSigpaeSerializer,
            204: None,
            502: dict,
        },
    )
    def get(self, _request: Request, codigo_rf: str) -> Response:
        """Retorna dados SIGPAE do funcionario.

        Args:
            codigo_rf: RF usado na consulta.

        Returns:
            Dados SIGPAE do funcionario, ou ausencia de dados.
        """
        if not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        try:
            data = services.get_funcionario_dados_sigpae(codigo_rf)
        except httpx.HTTPStatusError as exc:
            return api_error_response_status_livre(exc)
        if data is None:
            return Response(status=204)
        if not isinstance(data, dict):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(FuncionarioDadosSigpaeSerializer(data).data)


class EscolaFuncionariosCargoView(ProfessoresAPIView):
    """Retorna funcionários da escola filtrados por cargo."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        description=("Retorna funcionários da escola filtrados por cargo."),
        responses={200: FuncionarioEscolaSerializer(many=True), 204: None},
    )
    def get(
        self,
        _request: Request,
        codigo_ue: str,
        codigo_cargo: str,
    ) -> Response:
        """Retorna funcionários da escola filtrados por cargo.

        Args:
            codigo_ue: Código da unidade escolar usada na consulta.
            codigo_cargo: Código do cargo usado como filtro.

        Returns:
            Funcionários no cargo informado, ou ausência de conteúdo.
        """
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        if not codigo_cargo.strip():
            return detail_response("É necessário informar o codigoCargo.")
        data = services.get_funcionarios_escola_por_cargo(
            codigo_ue,
            codigo_cargo,
        )
        if data is None:
            return Response(status=204)
        return Response(FuncionarioEscolaSerializer(data, many=True).data)


class EscolaFuncionariosCargosView(ProfessoresAPIView):
    """Retorna funcionários da escola filtrados por cargos."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        description=("Retorna funcionários da escola filtrados por cargos."),
        parameters=[
            OpenApiParameter(
                "cargos",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "codigo_dre",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
            ),
        ],
        responses={200: FuncionarioCargoSerializer(many=True), 204: None},
    )
    def get(self, request: Request, codigo_ue: str) -> Response:
        """Retorna funcionários da escola filtrados por cargos.

        Args:
            request: Requisição com os cargos e a DRE de filtro.
            codigo_ue: Código da unidade escolar usada na consulta.

        Returns:
            Funcionários nos cargos informados, ou ausência de conteúdo.
        """
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        params = _query_params(request, {"cargos"}, {"dre_codigo"})
        data = services.get_funcionarios_escola_cargos(codigo_ue, params)
        if data is None:
            return Response(status=204)
        if not _is_lista_dicionarios(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(FuncionarioCargoSerializer(data, many=True).data)


class EscolaFuncionariosFuncoesAtividadesView(ProfessoresAPIView):
    """Retorna funcionários da escola por funções atividades."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        description=("Retorna funcionários da escola por funções atividades."),
        parameters=[
            OpenApiParameter(
                "funcoes_atividades",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "codigo_dre",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
            ),
        ],
        responses={
            200: FuncionarioFuncaoAtividadeSerializer(many=True),
            204: None,
        },
    )
    def get(self, request: Request, codigo_ue: str) -> Response:
        """Retorna funcionários da escola por funções atividades.

        Args:
            request: Requisição com as funções atividades e a DRE de filtro.
            codigo_ue: Código da unidade escolar usada na consulta.

        Returns:
            Funcionários nas funções atividades, ou ausência de conteúdo.
        """
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        params = _query_params(
            request,
            {"funcoes_atividades"},
            {"codigo_dre"},
        )
        data = services.get_funcionarios_escola_funcoes_atividades(
            codigo_ue,
            params,
        )
        if data is None:
            return Response(status=204)
        if not _is_lista_dicionarios(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(
            FuncionarioFuncaoAtividadeSerializer(data, many=True).data
        )


class EscolaFuncionariosFuncoesExternasView(ProfessoresAPIView):
    """Retorna funcionários da escola por funções externas."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        description=("Retorna funcionários da escola por funções externas."),
        parameters=[
            OpenApiParameter(
                "funcoes",
                int,
                OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
            OpenApiParameter(
                "codigo_dre",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
            ),
        ],
        responses={
            200: FuncionarioFuncaoExternaSerializer(many=True),
            204: None,
        },
    )
    def get(self, request: Request, codigo_ue: str) -> Response:
        """Retorna funcionários da escola por funções externas.

        Args:
            request: Requisição com as funções externas e a DRE de filtro.
            codigo_ue: Código da unidade escolar usada na consulta.

        Returns:
            Funcionários nas funções externas, ou ausência de conteúdo.
        """
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        params = _query_params(request, {"funcoes"}, {"codigo_dre"})
        if "codigo_dre" not in params:
            return Response(status=400)
        data = services.get_funcionarios_escola_funcoes_externas(
            codigo_ue,
            params,
        )
        if data is None:
            return Response(status=204)
        if not _is_lista_dicionarios(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(
            FuncionarioFuncaoExternaSerializer(data, many=True).data
        )


class EscolaFuncionariosFuncaoExternaView(ProfessoresAPIView):
    """Retorna funcionários da escola por uma função externa específica."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        description=("Retorna funcionários da escola por uma função externa."),
        responses={200: FuncionarioEscolaSerializer(many=True), 204: None},
    )
    def get(
        self,
        _request: Request,
        codigo_ue: str,
        codigo_funcao_externa: str,
    ) -> Response:
        """Retorna funcionários da escola por uma função externa específica.

        Args:
            codigo_ue: Código da unidade escolar usada na consulta.
            codigo_funcao_externa: Código da função externa usado como filtro.

        Returns:
            Funcionários da função externa, ou ausência de conteúdo.
        """
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        if not codigo_funcao_externa.strip():
            return detail_response(_MSG_CODIGO_FUNCAO_EXTERNA_OBRIGATORIO)
        data = services.get_funcionarios_escola_por_funcao_externa(
            codigo_ue,
            codigo_funcao_externa,
        )
        if not data:
            return Response(status=204)
        if not _is_lista_dicionarios(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(FuncionarioEscolaSerializer(data, many=True).data)


class EscolaFuncionariosFuncaoAtividadeView(ProfessoresAPIView):
    """Retorna funcionários da escola por uma função atividade específica."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        description=(
            "Retorna funcionários da escola por uma função atividade."
        ),
        responses={
            200: FuncionarioFuncaoAtividadeUeSerializer(many=True),
            204: None,
        },
    )
    def get(
        self,
        _request: Request,
        codigo_ue: str,
        codigo_funcao_atividade: str,
    ) -> Response:
        """Retorna funcionários da escola por uma função atividade específica.

        Args:
            codigo_ue: Código da unidade escolar usada na consulta.
            codigo_funcao_atividade: Código da função atividade usado como
                filtro.

        Returns:
            Funcionários da função atividade, ou ausência de conteúdo.
        """
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        if not codigo_funcao_atividade.strip():
            return detail_response(_MSG_CODIGO_FUNCAO_ATIVIDADE_OBRIGATORIO)
        data = services.get_funcionarios_escola_por_funcao_atividade(
            codigo_ue,
            codigo_funcao_atividade,
        )
        if not data:
            return Response(status=204)
        if not _is_lista_dicionarios(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(
            FuncionarioFuncaoAtividadeUeSerializer(data, many=True).data
        )


class EscolaFuncionariosView(ProfessoresAPIView):
    """Retorna funcionários vinculados à escola."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        description=("Retorna funcionários vinculados à escola."),
        responses={200: FuncionarioEscolaSerializer(many=True), 204: None},
    )
    def get(self, _request: Request, codigo_ue: str) -> Response:
        """Retorna funcionários vinculados à escola.

        Args:
            codigo_ue: Código da unidade escolar usada na consulta.

        Returns:
            Funcionários vinculados à escola, ou ausência de conteúdo.
        """
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        data = services.get_funcionarios_escola(codigo_ue)
        if data is None:
            return Response(status=204)
        return Response(FuncionarioEscolaSerializer(data, many=True).data)


class FuncionariosUeView(ProfessoresAPIView):
    """Retorna funcionários vinculados à unidade educacional."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna funcionários vinculados à unidade educacional."),
        request=BuscarFuncionariosPorUeSerializer,
        responses={
            200: FuncionarioUeLegadoSerializer(many=True),
            204: None,
            400: dict,
            404: str,
        },
    )
    def post(self, request: Request, codigo_ue: str) -> Response:
        """Retorna funcionários vinculados à unidade educacional.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_ue: Código da unidade educacional usada na consulta.

        Returns:
            Funcionários vinculados à unidade, ou ausência de conteúdo.
        """
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        serializer = BuscarFuncionariosPorUeSerializer(data=request.data or {})
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = services.get_funcionarios_ue(
            codigo_ue,
            serializer.validated_data,
        )
        if data is None:
            return Response(status=204)
        if not isinstance(data, list):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        if not data:
            return Response(
                "Não foram encontrados funcionários.",
                status=404,
            )
        return Response(FuncionarioUeLegadoSerializer(data, many=True).data)


class FuncionariosCargoView(ProfessoresAPIView):
    """Retorna funcionários vinculados ao cargo."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna funcionários vinculados ao cargo."),
        responses={200: FuncionarioEscolaSerializer(many=True), 204: None},
    )
    def get(self, _request: Request, codigo_cargo: str) -> Response:
        """Retorna funcionários vinculados ao cargo.

        Args:
            codigo_cargo: Código do cargo usado na consulta.

        Returns:
            Funcionários vinculados ao cargo, ou ausência de conteúdo.
        """
        if not codigo_cargo.strip():
            return detail_response("É necessário informar o codigoCargo.")
        data = services.get_funcionarios_por_cargo(codigo_cargo)
        if data is None:
            return Response(status=204)
        if not isinstance(data, list):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(FuncionarioEscolaSerializer(data, many=True).data)


class FuncionariosSupervisoresView(ProfessoresAPIView):
    """Retorna supervisores vinculados à DRE."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna supervisores vinculados à DRE."),
        request=ListaStringSerializer,
        responses={
            200: SupervisorLegadoSerializer(many=True),
            400: str,
            404: str,
        },
    )
    def post(self, request: Request, codigo_dre: str) -> Response:
        """Retorna supervisores vinculados à DRE.

        Args:
            request: Requisição HTTP recebida pela API.
            codigo_dre: Código EOL da DRE consultada.

        Returns:
            Supervisores vinculados à DRE informada.
        """
        serializer = ListaStringSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                _MSG_LISTA_SUPERVISORES_OBRIGATORIA,
                status=400,
            )
        data = services.get_supervisores_por_dre(
            codigo_dre,
            serializer.validated_data,
        )
        if data is None:
            return Response(status=204)
        if not isinstance(data, list):
            return Response(
                {
                    "detail": _MSG_RESPOSTA_INVALIDA_API,
                    "api": data,
                },
                status=502,
            )
        if not data:
            return Response(_MSG_SUPERVISORES_NAO_ENCONTRADOS, status=404)
        return Response(SupervisorLegadoSerializer(data, many=True).data)


class DRESupervisoresView(ProfessoresAPIView):
    """Retorna supervisores vinculados a DRE."""

    @extend_schema(
        tags=_TAG_DRE,
        description=("Retorna supervisores vinculados a DRE."),
        responses={200: SupervisorLegadoSerializer(many=True), 502: dict},
    )
    def get(self, _request: Request, codigo_eol_dre: str) -> Response:
        """Retorna supervisores vinculados a DRE.

        Args:
            codigo_eol_dre: Codigo EOL da DRE consultada.

        Returns:
            Supervisores vinculados a DRE informada.
        """
        if not codigo_eol_dre.strip():
            return Response([])
        try:
            data = services.get_supervisores_dre(codigo_eol_dre)
        except httpx.HTTPStatusError as exc:
            return api_error_response_status_livre(exc)
        if data is None:
            return Response([])
        if not _is_lista_dicionarios(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(SupervisorLegadoSerializer(data, many=True).data)


class FuncionariosPerfisView(ProfessoresAPIView):
    """Retorna usuários SGP por perfil."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna usuários SGP por perfil."),
        parameters=_PARAMS_FUNCIONARIOS_PERFIL,
        responses={
            200: FuncionarioSgpLegadoSerializer(many=True),
            400: str,
            404: str,
        },
    )
    def get(self, request: Request, id_perfil: str) -> Response:
        """Retorna usuários SGP por perfil.

        Args:
            request: Requisição com filtros de perfil.
            id_perfil: Perfil usado na consulta.

        Returns:
            Usuários SGP encontrados para o perfil.
        """
        if not id_perfil.strip():
            return detail_response(_MSG_PERFIL_OBRIGATORIO)
        params = {
            "codigo_dre": (
                request.query_params.get("CodigoDre")
                or request.query_params.get("codigo_dre")
            ),
            "codigo_ue": (
                request.query_params.get("CodigoUe")
                or request.query_params.get("codigo_ue")
            ),
            "codigo_rf": (
                request.query_params.get("CodigoRf")
                or request.query_params.get("codigo_rf")
            ),
            "nome_servidor": (
                request.query_params.get("NomeServidor")
                or request.query_params.get("nome_servidor")
            ),
        }
        params = {chave: valor for chave, valor in params.items() if valor}
        data = services.get_usuarios_sgp_por_perfil(id_perfil, params)
        if data is None:
            return Response(status=204)
        if not isinstance(data, list):
            return Response(data, status=400)
        return Response(FuncionarioSgpLegadoSerializer(data, many=True).data)


class FuncionariosPerfisDreView(ProfessoresAPIView):
    """Retorna funcionários SGP por perfil e DRE."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna funcionários SGP por perfil e DRE."),
        parameters=[
            _PARAM_CODIGO_UE_LEGADO,
            _PARAM_CODIGO_RF_LEGADO,
            _PARAM_NOME_SERVIDOR_LEGADO,
        ],
        responses={
            200: FuncionarioSgpLegadoSerializer(many=True),
            400: str,
            404: str,
        },
    )
    def get(
        self,
        request: Request,
        id_perfil: str,
        codigo_dre: str,
    ) -> Response:
        """Retorna funcionários SGP por perfil e DRE.

        Args:
            request: Requisição com filtros de perfil.
            id_perfil: Perfil usado na consulta.
            codigo_dre: DRE usada na consulta.

        Returns:
            Funcionários SGP encontrados para a DRE.
        """
        if not id_perfil.strip():
            return detail_response(_MSG_PERFIL_OBRIGATORIO)
        if not codigo_dre.strip():
            return detail_response("É necessário informar o codigoDre.")
        params = {
            "codigo_ue": (
                request.query_params.get("CodigoUe")
                or request.query_params.get("codigo_ue")
            ),
            "codigo_rf": (
                request.query_params.get("CodigoRf")
                or request.query_params.get("codigo_rf")
            ),
            "nome_servidor": (
                request.query_params.get("NomeServidor")
                or request.query_params.get("nome_servidor")
            ),
        }
        params = {chave: valor for chave, valor in params.items() if valor}
        data = services.get_funcionarios_sgp_por_perfil_dre(
            id_perfil,
            codigo_dre,
            params,
        )
        if data is None:
            return Response(status=204)
        if not isinstance(data, list):
            return Response(data, status=400)
        return Response(FuncionarioSgpLegadoSerializer(data, many=True).data)


class ProfessorDisciplinaTurmasView(ProfessoresAPIView):
    """Retorna turmas atribuídas ao professor."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Retorna turmas do professor para a disciplina.\n\n"
            "RequestBody: `turmas_ids`."
        ),
        request={
            "application/json": {
                "type": "array",
                "items": {"type": "string"},
                "description": "turmas_ids",
            }
        },
        responses={200: ProfessorTurmaSerializer(many=True), 204: None},
    )
    def post(
        self,
        request: Request,
        codigo_rf: str,
        disciplina_id: str,
    ) -> Response:
        """Retorna turmas do professor para a disciplina.

        Args:
            request: Requisição com as turmas consultadas no corpo.
            codigo_rf: RF usado na consulta.
            disciplina_id: Disciplina usada como filtro.

        Returns:
            Turmas atribuídas ao professor, ou ausência de conteúdo.

        Raises:
            ValidationError: Quando as turmas informadas são inválidas.
        """
        if not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        if not disciplina_id.strip():
            return detail_response("É necessário informar a disciplina.")
        serializer = TurmasIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = services.get_turmas_professor_disciplina(
            codigo_rf,
            disciplina_id,
            serializer.validated_data,
        )
        if data is None:
            return Response(status=204)
        if not _is_lista_turmas(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(ProfessorTurmaSerializer(data, many=True).data)


class ProfessorTurmasView(ProfessoresAPIView):
    """Retorna turmas atribuídas ao professor."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=("Retorna turmas atribuídas ao professor pelo RF."),
        responses={
            200: TurmaAtribuidaProfessorSerializer(many=True),
            204: None,
        },
    )
    def get(self, _request: Request, codigo_rf: str) -> Response:
        """Retorna turmas atribuídas ao professor pelo RF.

        Args:
            codigo_rf: RF usado na consulta.

        Returns:
            Turmas atribuídas ao professor, ou ausência de conteúdo.
        """
        if not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        data = services.montar_turmas_atribuidas_professor(codigo_rf)
        if not data:
            return Response(status=204)
        return Response(
            TurmaAtribuidaProfessorSerializer(data, many=True).data
        )


class FuncionarioPerfilTurmasView(ProfessoresAPIView):
    """Retorna abrangência de turmas do funcionário."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna abrangência de turmas do funcionário."),
        parameters=_PARAMS_TURMAS_TEMPORARIOS,
        responses={200: OpenApiTypes.OBJECT, 204: None},
    )
    def get(self, request: Request, login: str, id_perfil: str) -> Response:
        """Retorna abrangência de turmas do funcionário.

        Args:
            request: Requisição com os parâmetros temporários de abrangência.
            login: Login usado na consulta.
            id_perfil: Perfil usado na consulta.

        Returns:
            Abrangência de turmas, ou ausência de conteúdo.
        """
        if not login.strip():
            return detail_response("É necessário informar o login.")
        if not id_perfil.strip():
            return detail_response(_MSG_PERFIL_OBRIGATORIO)
        params = _abrangencia_temporaria(request)
        data = services.get_abrangencia_funcionario_perfil(
            login,
            id_perfil,
            abrangencia=params.abrangencia,
            cargos=params.cargos,
            funcoes=params.funcoes,
            grupo=params.grupo,
            dre_codigo=params.dre_codigo,
            eh_perfil_manual=params.eh_perfil_manual,
        )
        if data is None:
            return Response(status=204)
        return Response(data)


class FuncionariosTurmasView(ProfessoresAPIView):
    """Retorna abrangência de turmas para unidades."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna abrangência de turmas para unidades."),
        request=ListaStringSerializer,
        responses={200: OpenApiTypes.OBJECT, 204: None},
    )
    def post(self, request: Request) -> Response:
        """Retorna abrangência de turmas para unidades.

        Args:
            request: Requisição com a lista de UEs no corpo.

        Returns:
            Abrangência de turmas, ou ausência de conteúdo.

        Raises:
            ValidationError: Quando a lista de UEs informada é inválida.
        """
        serializer = ListaStringSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = services.get_abrangencia_ues(serializer.validated_data)
        if data is None:
            return Response(status=204)
        return Response(data)


class FuncionariosBuscarTurmasElegiveisView(ProfessoresAPIView):
    """Retorna turmas elegíveis para cópia."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna turmas elegíveis para cópia."),
        request=BuscarTurmasElegiveisSerializer,
        responses={200: OpenApiTypes.OBJECT, 204: None},
    )
    def post(self, request: Request) -> Response:
        """Retorna turmas elegíveis para cópia.

        Args:
            request: Requisição com os dados da consulta.

        Returns:
            Turmas elegíveis, ou ausência de conteúdo.
        """
        payload = cast(dict[str, Any], request.data)
        data = services.get_turmas_elegiveis(payload)
        if not data:
            return Response(status=204)
        return Response(data)


class FuncionariosView(ProfessoresAPIView):
    """Retorna funcionários por filtros básicos."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna funcionários por filtros básicos."),
        request=BuscarFuncionariosPorUeSerializer,
        responses={200: OpenApiTypes.OBJECT, 204: None},
    )
    def post(self, request: Request) -> Response:
        """Retorna funcionários por filtros básicos.

        Args:
            request: Requisição com os filtros no corpo.

        Returns:
            Funcionários encontrados, ou ausência de conteúdo.
        """
        payload = cast(dict[str, Any], request.data)
        data = services.get_funcionarios(payload)
        if data is None:
            return Response(status=204)
        if data == []:
            return Response(
                "Não foram encontrados funcionários.",
                status=404,
            )
        return Response(data)


class ProfessorBuscarPorRfDreUeView(ProfessoresAPIView):
    """Retorna dados resumidos de professor por RF, DRE e UE."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=("Retorna professor por RF, DRE e UE no ano letivo."),
        parameters=[
            OpenApiParameter(
                "dre_id",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                "ue_id",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                "buscar_outros_cargos",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses={200: ProfessorBuscarPorRfSerializer, 204: None},
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        ano_letivo: int,
    ) -> Response:
        """Retorna professor por RF, DRE e UE no ano letivo.

        Args:
            request: Requisição com os filtros opcionais de DRE e UE.
            codigo_rf: RF usado na consulta.
            ano_letivo: Ano letivo de referência.

        Returns:
            Dados resumidos do professor, ou ausência de conteúdo.
        """
        if not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        params = _query_params(
            request,
            set(),
            {"dre_id", "ue_id", "buscar_outros_cargos"},
        )
        data = services.get_professor_por_rf_dre_ue(
            codigo_rf,
            ano_letivo,
            params,
        )
        if data is None:
            return Response(status=204)
        return Response(ProfessorBuscarPorRfSerializer(data).data)


class ProfessoresBuscarPorListaRfAnoView(ProfessoresAPIView):
    """Retorna professores pelos RFs informados no ano letivo."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=("Retorna professores pelos RFs informados no ano."),
        request=ListaStringSerializer,
        responses={200: ProfessorBuscarPorRfSerializer(many=True), 204: None},
    )
    def post(self, request: Request, ano_letivo: int) -> Response:
        """Retorna professores pelos RFs no ano letivo.

        Args:
            request: Requisição com a lista de RFs no corpo.
            ano_letivo: Ano letivo de referência.

        Returns:
            Professores encontrados, ou ausência de conteúdo.

        Raises:
            ValidationError: Quando a lista de RFs informada é inválida.
        """
        if isinstance(request.data, list) and not request.data:
            return detail_response("É necessário informar ao menos um RF.")
        serializer = ListaStringSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = services.get_professores_por_lista_rf_ano(
            ano_letivo,
            serializer.validated_data,
        )
        if data is None:
            return Response(status=204)
        return Response(ProfessorBuscarPorRfSerializer(data, many=True).data)


class ProfessorEhEmeiView(ProfessoresAPIView):
    """Retorna indicação de vínculo do professor com EMEI."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=("Retorna booleano indicando se o professor é EMEI."),
        responses={200: OpenApiTypes.BOOL},
    )
    def get(self, _request: Request, codigo_rf: str) -> Response:
        """Retorna booleano de vínculo do professor com EMEI.

        Args:
            codigo_rf: RF usado na consulta.

        Returns:
            Indicador booleano de vínculo com EMEI.
        """
        if not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        data = services.get_eh_emei(codigo_rf)
        return Response(data)


class ProfessorAutoCompleteView(ProfessoresAPIView):
    """Lista professores para autocomplete por DRE e ano letivo."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=("Lista professores para autocomplete por DRE e ano."),
        parameters=[
            OpenApiParameter(
                "ue_id",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
            ),
            OpenApiParameter(
                "nome",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
            ),
        ],
        responses={
            200: ProfessorAutoCompleteSerializer(many=True),
            204: None,
        },
    )
    def get(
        self,
        request: Request,
        ano_letivo: int,
        dre_id: str,
    ) -> Response:
        """Lista professores para autocomplete por DRE e ano letivo.

        Args:
            request: Requisição com os filtros obrigatórios de UE e nome.
            ano_letivo: Ano letivo de referência.
            dre_id: Identificador da DRE usado na consulta.

        Returns:
            Professores encontrados, ou ausência de conteúdo.
        """
        if not dre_id.strip():
            return detail_response(_MSG_DRE_ID_OBRIGATORIO)
        ue_id = request.query_params.get("ue_id")
        if not ue_id or not ue_id.strip():
            return detail_response(_MSG_UE_ID_OBRIGATORIO)
        nome = request.query_params.get("nome")
        if not nome or not nome.strip():
            return detail_response(_MSG_NOME_OBRIGATORIO)
        if len(nome.strip()) < _TAMANHO_MINIMO_NOME:
            return Response(status=204)
        params = _query_params(request, set(), {"ue_id", "nome"})
        data = services.get_autocomplete_professores(
            ano_letivo,
            dre_id,
            params,
        )
        if not data:
            return Response([])
        if not _is_lista_dicionarios(data):
            return detail_response(_MSG_RESPOSTA_INVALIDA_API, 502)
        return Response(ProfessorAutoCompleteSerializer(data, many=True).data)


class ProfessorBuscaTurmasAtribuidasEscolaView(ProfessoresAPIView):
    """Retorna turmas atribuídas ao professor na escola."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Retorna turmas atribuídas ao professor na escola no ano letivo."
        ),
        responses={
            200: ProfessorTurmaAtribuidaSimplificadaSerializer(many=True),
            404: _MSG_TURMAS_NAO_ENCONTRADAS,
        },
    )
    def get(
        self,
        request: Request,
        codigo_eol_escola: str,
        ano_letivo: int,
        codigo_rf: str | None = None,
    ) -> Response:
        """Retorna turmas atribuídas ao professor na escola.

        Args:
            request: Requisição com os filtros opcionais de RF.
            codigo_eol_escola: Código EOL da escola usada na consulta.
            ano_letivo: Ano letivo de referência.
            codigo_rf: RF usado na consulta (opcional).

        Returns:
            Turmas atribuídas ao professor na escola, ou ausência de conteúdo.
        """
        if not codigo_rf or not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        if not codigo_eol_escola.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        data = services.get_turmas_atribuidas_professor_escola(
            codigo_rf, codigo_eol_escola, ano_letivo
        )
        if not data:
            return Response(
                status=404,
                data=_MSG_TURMAS_NAO_ENCONTRADAS,
            )
        return Response(
            ProfessorTurmaAtribuidaSimplificadaSerializer(data, many=True).data
        )


class BuscaTurmasAtribuidasProfessoresEscolaView(ProfessoresAPIView):
    """Retorna turmas atribuídas a professores na escola."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Retorna turmas atribuídas a professores na escola no ano letivo."
        ),
        responses={
            200: ProfessorTurmaAtribuidaSimplificadaSerializer(many=True),
            404: _MSG_TURMAS_NAO_ENCONTRADAS,
        },
    )
    def get(
        self, request: Request, codigo_eol_escola: str, ano_letivo: int
    ) -> Response:
        """Retorna turmas atribuídas a professores na escola.

        Args:
            request: Requisição com os filtros opcionais de RF.
            codigo_eol_escola: Código EOL da escola usada na consulta.
            ano_letivo: Ano letivo de referência.
            codigo_rf: RF usado na consulta (opcional).

        Returns:
            Turmas atribuídas a professores na escola, ou ausência de conteúdo.
        """
        if not codigo_eol_escola.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        data = services.get_turmas_atribuidas_professores_escola(
            codigo_eol_escola,
            ano_letivo,
        )
        if not data:
            return Response(status=404, data=_MSG_TURMAS_NAO_ENCONTRADAS)
        return Response(
            ProfessorTurmaAtribuidaSimplificadaSerializer(data, many=True).data
        )


class ProfessorBuscarTurmasAtribuidasView(ProfessoresAPIView):
    """Retorna turmas atribuídas ao professor."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=("Retorna turmas atribuídas ao professor no ano letivo."),
        responses={
            200: ProfessorTurmaAtribuidaSimplificadaSerializer(many=True),
            404: _MSG_TURMAS_NAO_ENCONTRADAS,
        },
    )
    def get(
        self,
        request: Request,
        codigo_rf: str,
        ano_letivo: int,
    ) -> Response:
        """Retorna turmas atribuídas ao professor.

        Args:
            request: Requisição com os filtros opcionais de RF.
            codigo_rf: RF usado na consulta.
            ano_letivo: Ano letivo de referência.

        Returns:
            Turmas atribuídas ao professor, ou ausência de conteúdo.
        """
        if not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        data = services.get_turmas_atribuidas_professor(codigo_rf, ano_letivo)
        if not data:
            return Response(status=404, data=_MSG_TURMAS_NAO_ENCONTRADAS)
        return Response(
            ProfessorTurmaAtribuidaSimplificadaSerializer(data, many=True).data
        )


class AdministradorSgpEscolaView(ProfessoresAPIView):
    """Retorna administradores SGP da escola."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        operation_id="E01_administrador_sgp",
        description=(
            "Retorna lista de RFs dos administradores SGP da escola "
            "(ADM UE e ADM DRE)."
        ),
        responses={
            200: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request: Request, codigo_ue: str) -> Response:
        """Retorna administradores SGP da escola.

        Args:
            request: Requisição HTTP.
            codigo_ue: Código EOL da unidade educacional.

        Returns:
            Array de RFs dos administradores: ["7821972", "7980302", ...]
            ou array vazio [] se não houver.
        """
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        data = services.get_administradores_sgp_escola(codigo_ue)
        return Response(data)
