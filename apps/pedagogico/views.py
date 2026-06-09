"""Views do domínio pedagógico."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pedagogico import services
from apps.pedagogico.serializers import (
    CodigoTurmaListSerializer,
    ComponenteBaseSerializer,
    ComponenteCurricularSerializer,
    ComponenteRegenciaSerializer,
    DadosAulaTurmaSerializer,
    GradeCurricularSerializer,
    TurmaDadosSerializer,
)

_TAG = ["ComponenteCurricular"]
_TAG_TURMA = ["Turma"]
_TURMA_REQUEST_SCHEMA = {
    "type": "array",
    "items": {"type": "string"},
    "description": (
        "Body opcional com `codigos_turmas`; informe uma lista JSON de "
        "codigos de turmas."
    ),
}


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
            componentes_curriculares=request.query_params.getlist(
                "componentesCurriculares"
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
