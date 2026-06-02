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
