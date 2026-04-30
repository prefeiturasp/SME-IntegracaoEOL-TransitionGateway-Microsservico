"""Views do domínio pedagógico — tradução dos contratos legados L1–L17."""

from typing import cast

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pedagogico import services
from apps.pedagogico.serializers import (
    AgrupamentoTerritorioSerializer,
    ComponenteBaseSerializer,
    ComponenteCurricularSerializer,
    ComponenteRegenciaSerializer,
    ComponenteVigenciaSerializer,
    GradeCurricularSerializer,
)

_TAG = ["Componentes Curriculares"]

_ARRAY_IDS = {
    "application/json": {
        "type": "array",
        "items": {"type": "integer", "format": "int64"},
    }
}


class ComponentesFuncionarioComTurmaView(APIView):
    """Legado L1."""

    @extend_schema(
        tags=_TAG,
        summary="[L1] Componentes do funcionário por turma com agrupamento",
        description=(
            "Retorna componentes curriculares de um funcionário "
            "filtrados por turma. "
            "O flag `agrupaComponenteCurricular` controla o agrupamento "
            "por `codigoComponenteCurricularPai`.\n\n"
            "Internamente mapeia para "
            "**EP-1** `GET /funcionarios/{login}`."
        ),
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(
        self,
        _request: Request,
        cod: str,
        login: str,
        id_perfil: str,
        flag: str,
    ) -> Response:
        data = services.get_componentes_funcionario(
            login=login,
            id_perfil=id_perfil,
            codigo_turma=cod,
            agrupa=(flag.lower() == "true") if flag else False,
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesFuncionarioView(APIView):
    """Legado L2."""

    @extend_schema(
        tags=_TAG,
        summary="[L2] Componentes do funcionário sem filtro de turma",
        description=(
            "Retorna todos os componentes curriculares de um funcionário, "
            "sem filtro de turma.\n\n"
            "Internamente mapeia para "
            "**EP-1** `GET /funcionarios/{login}`."
        ),
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(self, _request: Request, login: str, id_perfil: str) -> Response:
        data = services.get_componentes_funcionario(
            login=login,
            id_perfil=id_perfil,
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesPlanejamentoFuncionarioView(APIView):
    """Legado L3."""

    @extend_schema(
        tags=_TAG,
        summary="[L3] Componentes do funcionário com planejamento de regência",
        description=(
            "Retorna componentes de uma turma substituindo os de regência "
            "pelos filhos de planejamento (`planejamentoRegencia=true`).\n\n"
            "Internamente mapeia para "
            "**EP-1** `GET /funcionarios/{login}?planejamento=true`."
        ),
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(
        self, request: Request, cod: str, login: str, id_perfil: str
    ) -> Response:
        data = services.get_componentes_funcionario(
            login=login,
            id_perfil=id_perfil,
            codigo_turma=cod,
            planejamento=True,
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesRegenciaView(APIView):
    """Legado L4."""

    @extend_schema(
        tags=_TAG,
        summary="[L4] Componentes de regência por ano de turma",
        description=(
            "Retorna os componentes curriculares de regência para o "
            "ano de turma informado. "
            "Quando `anoTurma <= 0`, retorna componentes"
            " com `ano IS NULL`.\n\n"
            "Somente `codigo` e `descricao` são preenchidos; "
            "os demais campos refletem os valores padrão do legado.\n\n"
            "Internamente mapeia para "
            "**EP-2** `GET /anos/{anoTurma}/regencia`."
        ),
        responses={200: ComponenteRegenciaSerializer(many=True)},
    )
    def get(self, request: Request, ano_turma: int) -> Response:
        data = services.get_componentes_regencia(ano_turma)
        return Response(ComponenteRegenciaSerializer(data, many=True).data)


class ValidarPapView(APIView):
    """Legado L5."""

    @extend_schema(
        tags=_TAG,
        summary="[L5] Verificar componente PAP em turma",
        description=(
            "Verifica se o funcionário possui ao menos um componente "
            "PAP (Programa de Acompanhamento Pedagógico) na turma.\n\n"
            "Internamente mapeia para "
            "**EP-3** `GET /turmas/{codigoTurma}/pap`."
        ),
        responses={200: OpenApiTypes.BOOL},
    )
    def get(
        self, request: Request, cod: str, login: str, id_perfil: str
    ) -> Response:
        data = services.validar_pap(
            codigo_turma=cod,
            login=login,
            id_perfil=id_perfil,
        )
        return Response(data)


class ComponentesUeAnosEscolaresView(APIView):
    """Legado L6."""

    @extend_schema(
        tags=_TAG,
        summary="[L6] Componentes por UE, modalidade, ano e anos escolares",
        description=(
            "Retorna componentes da grade de oferta filtrados pelos "
            "anos escolares informados via query param `anosEscolares`.\n\n"
            "**Modalidades:** 1=EI, 3=EJA, 4=CIEJA, 5=EF, 6=EM.\n\n"
            "Internamente mapeia para "
            "**EP-4** `GET /ues/{id}/modalidades/{mod}/anos/{ano}`."
        ),
        parameters=[
            OpenApiParameter(
                "anosEscolares",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
                description='Anos escolares (ex.: `["1","2","3"]`).',
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(self, request: Request, id: str, mod: int, ano: int) -> Response:
        data = services.get_componentes_ue_anos(
            ue_id=id,
            modalidade=mod,
            ano_letivo=ano,
            anos_escolares=request.query_params.getlist("anosEscolares"),
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesUeModalidadeView(APIView):
    """Legado L7."""

    @extend_schema(
        tags=_TAG,
        summary="[L7] Componentes de turmas programa por UE e modalidade",
        description=(
            "Retorna componentes de turmas programa (projetos especiais) "
            "para UE + modalidade + ano letivo, sem filtro de ano escolar.\n\n"
            "**Modalidades:** 1=EI, 3=EJA, 4=CIEJA, 5=EF, 6=EM.\n\n"
            "Internamente mapeia para "
            "**EP-5** "
            "`GET /ues/{id}/modalidades/{mod}/anos/{ano}/turmas-programa`."
        ),
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(self, request: Request, id: str, mod: int, ano: int) -> Response:
        data = services.get_componentes_turmas_programa(
            ue_id=id,
            modalidade=mod,
            ano_letivo=ano,
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesPorTurmasUeView(APIView):
    """Legado L8."""

    @extend_schema(
        tags=_TAG,
        summary="[L8] Componentes por lista de turmas e UE",
        description=(
            "Retorna componentes das turmas informadas, consolidando "
            "agrupamentos de Território do Saber. "
            "Componentes com `codigo=0` são descartados. "
            "Retorna DTO simplificado ordenado alfabeticamente.\n\n"
            "Internamente mapeia para "
            "**EP-6** `GET /ues/{id}/turmas`."
        ),
        parameters=[
            OpenApiParameter(
                "turmas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
                description="Lista de códigos de turmas.",
            ),
        ],
        responses={200: ComponenteBaseSerializer(many=True)},
    )
    def get(self, request: Request, id: str) -> Response:
        data = services.get_componentes_por_turmas_ue(
            ue_id=id,
            turmas=request.query_params.getlist("turmas"),
        )
        return Response(ComponenteBaseSerializer(data, many=True).data)


class ComponentesPlanejamentoView(APIView):
    """Legado L9."""

    @extend_schema(
        tags=_TAG,
        summary="[L9] Componentes para planejamento por lista de turmas",
        description=(
            "Retorna componentes de múltiplas turmas com processamento "
            "de Território do Saber e expansão de planejamento de "
            "regência (padrão ativo).\n\n"
            "Internamente mapeia para **EP-7** `GET /turmas`."
        ),
        parameters=[
            OpenApiParameter(
                "codigoTurmas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
                description="Lista de códigos de turmas.",
            ),
            OpenApiParameter(
                "adicionarComponentesPlanejamento",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Substitui regência pelos filhos de planejamento. "
                    "Padrão: `true`."
                ),
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        data = services.get_componentes_planejamento(
            codigo_turmas=request.query_params.getlist("codigoTurmas"),
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class ComponentesRegularesView(APIView):
    """Legado L10."""

    @extend_schema(
        tags=_TAG,
        summary="[L10] Componentes de turmas sem pós-processamento",
        description=(
            "Retorna componentes das turmas **sem** processamento de "
            "Território do Saber nem expansão de planejamento. "
            "Deduplicação por `codigo` apenas.\n\n"
            "Internamente mapeia para "
            "**EP-8** `GET /turmas/brutos`."
        ),
        parameters=[
            OpenApiParameter(
                "codigoTurmas",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
                description="Lista de códigos de turmas.",
            ),
        ],
        responses={200: ComponenteCurricularSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        data = services.get_componentes_brutos(
            codigo_turmas=request.query_params.getlist("codigoTurmas"),
        )
        return Response(ComponenteCurricularSerializer(data, many=True).data)


class CatalogoComponentesView(APIView):
    """Legado L11."""

    @extend_schema(
        tags=_TAG,
        summary="[L11] Catálogo de componentes curriculares",
        description=(
            "Retorna todos os componentes curriculares ativos do EOL, "
            "sem filtro. Usado para popular dropdowns e listas.\n\n"
            "Internamente mapeia para **EP-9** `GET /`."
        ),
        responses={200: ComponenteBaseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        data = services.get_catalogo_componentes()
        return Response(ComponenteBaseSerializer(data, many=True).data)


class DadosAulaTurmaView(APIView):
    """Legado L12."""

    @extend_schema(
        tags=_TAG,
        summary="[L12] Dados de aula por turma (vigência de componentes)",
        description=(
            "Retorna a data de início de vigência de cada componente "
            "nas turmas da UE. "
            "Usado pelo módulo de registro de aulas.\n\n"
            "Para EJA/CIEJA, `semestre` filtra por `tipo_periodicidade`; "
            "para demais modalidades, o filtro não é aplicado.\n\n"
            "Internamente mapeia para "
            "**EP-10** `GET /turmas/vigencia`."
        ),
        parameters=[
            OpenApiParameter(
                "ueCodigo",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                description="Código da Unidade Educacional.",
            ),
            OpenApiParameter(
                "anoLetivo",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=True,
                description="Ano letivo (ex.: 2024).",
            ),
            OpenApiParameter(
                "componentesCurriculares",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
                description="Códigos dos componentes a consultar.",
            ),
            OpenApiParameter(
                "semestre",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=False,
                description="Semestre (1 ou 2). Aplicável para EJA.",
            ),
        ],
        responses={200: ComponenteVigenciaSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        p = request.query_params
        data = services.get_vigencia_componentes(
            ue_codigo=p.get("ueCodigo"),
            ano_letivo=p.get("anoLetivo"),
            componentes=p.getlist("componentesCurriculares"),
            semestre=p.get("semestre"),
        )
        return Response(ComponenteVigenciaSerializer(data, many=True).data)


class AnoTurmaAnoLetivoView(APIView):
    """Legado L16."""

    @extend_schema(
        tags=_TAG,
        summary="[L16] Grade curricular por ano letivo",
        description=(
            "Retorna todos os componentes da grade curricular para o "
            "ano letivo, agrupados por série e modalidade. "
            "Inclui todas as modalidades: "
            "1=EI, 3=EJA, 4=CIEJA, 5=EF, 6=EM.\n\n"
            "Internamente mapeia para "
            "**EP-11** `GET /grade-curricular/{anoLetivo}`."
        ),
        responses={200: GradeCurricularSerializer(many=True)},
    )
    def get(self, request: Request, ano_letivo: int) -> Response:
        data = services.get_grade_curricular(ano_letivo)
        return Response(GradeCurricularSerializer(data, many=True).data)


class ComponentesSemAtribuicaoView(APIView):
    """Legado L17."""

    @extend_schema(
        tags=_TAG,
        summary="[L17] Componentes sem atribuição em uma turma",
        description=(
            "Retorna as **descrições** dos componentes sem professor "
            "atribuído ou com atribuição não vigente na data informada "
            "(formato ticks .NET).\n\n"
            "Internamente mapeia para "
            "**EP-12** `GET /turmas/{cod}/sem-atribuicao?dataBase=`."
        ),
        responses={200: OpenApiTypes.STR},
    )
    def get(self, request: Request, cod: str, data_base_tick: str) -> Response:
        data = services.get_sem_atribuicao(
            codigo_turma=cod,
            data_base_tick=data_base_tick,
        )
        return Response(data)


class AgrupamentosCorrelacionadosView(APIView):
    """Legado L13."""

    @extend_schema(
        tags=_TAG,
        summary=("[L13] Agrupamentos correlacionados de Território do Saber"),
        description=(
            "Retorna agrupamentos de Território do Saber correlacionados "
            "ao componente: aqueles cujos componentes são subconjunto "
            "dos componentes do agrupamento de origem.\n\n"
            "Versão em lote: **L14**.\n\n"
            "Internamente mapeia para "
            "**EP-13** "
            "`GET /{cod}/territorio-saber/agrupamentos-correlacionados`."
        ),
        parameters=[
            OpenApiParameter(
                "dataBase",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Data de referência em ticks .NET. "
                    "Quando ausente, sem filtro de data."
                ),
            ),
        ],
        responses={200: AgrupamentoTerritorioSerializer(many=True)},
    )
    def get(self, request: Request, codigo_componente: int) -> Response:
        data = services.get_agrupamentos_correlacionados(
            codigo=codigo_componente,
            data_base=request.query_params.get("dataBase"),
        )
        return Response(AgrupamentoTerritorioSerializer(data, many=True).data)


class AgrupamentosCorrelacionadosLoteView(APIView):
    """Legado L14."""

    @extend_schema(
        tags=_TAG,
        summary=(
            "[L14] Agrupamentos correlacionados de Território do Saber "
            "(em lote)"
        ),
        description=(
            "Versão em lote do L13: recebe múltiplos IDs no corpo e "
            "retorna correlacionados de todos, consolidados em lista "
            "deduplicada por `cod_agrupamento`.\n\n"
            "Internamente mapeia para "
            "**EP-14** "
            "`POST /territorio-saber/agrupamentos-correlacionados`."
        ),
        parameters=[
            OpenApiParameter(
                "dataBase",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Data de referência em ticks .NET. "
                    "Quando ausente, sem filtro de data."
                ),
            ),
        ],
        request=_ARRAY_IDS,
        responses={200: AgrupamentoTerritorioSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        data = services.get_agrupamentos_correlacionados_lote(
            ids=cast(list[int], request.data),
            data_base=request.query_params.get("dataBase"),
        )
        return Response(AgrupamentoTerritorioSerializer(data, many=True).data)


class AgrupamentosTerritorioView(APIView):
    """Legado L15."""

    @extend_schema(
        tags=_TAG,
        summary="[L15] Agrupamentos de Território do Saber por IDs",
        description=(
            "Retorna os agrupamentos correspondentes aos IDs, sem expandir "
            "correlações. Diferente do L14, não busca subconjuntos.\n\n"
            "Internamente mapeia para "
            "**EP-15** `POST /territorio-saber/agrupamentos`."
        ),
        request=_ARRAY_IDS,
        responses={200: AgrupamentoTerritorioSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        data = services.get_agrupamentos(cast(list[int], request.data))
        return Response(AgrupamentoTerritorioSerializer(data, many=True).data)
