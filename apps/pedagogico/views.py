"""Views do domínio pedagógico."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pedagogico import services
from apps.pedagogico.serializers import (
    ComponenteBaseSerializer,
    ComponenteCurricularSerializer,
    GradeCurricularSerializer,
)

_TAG = ["ComponenteCurricular"]


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
        data = services.get_componentes_turmas_programa(
            ue_id=ue_id,
            modalidade=modalidade,
            ano_letivo=ano_letivo,
        )
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
        data = services.get_grade_curricular(ano_letivo)
        return Response(GradeCurricularSerializer(data, many=True).data)
