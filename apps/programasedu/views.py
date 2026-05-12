"""Views do dominio programas educacionais - contratos legados L1-L4."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.core.responses import Response, detail_response
from apps.programasedu import services
from apps.programasedu.serializers import (
    AlunoTurmaPapSerializer,
    AlunoTurmaProgramaPapSerializer,
    TurmaPapResumoSerializer,
)

_TAG = ["Programas Educacionais"]


class ObterTurmasPapView(APIView):
    """Lista turmas PAP por ano letivo e UE."""

    @extend_schema(
        tags=_TAG,
        description=(
            "Lista turmas PAP por ano letivo e UE."
        ),
        responses={200: TurmaPapResumoSerializer(many=True)},
    )
    def get(
        self, _request: Request, anoLetivo: int, codigoEscola: str
    ) -> Response:
        if not codigoEscola.strip():
            return detail_response("E necessario informar o codigoEscola.")
        data = services.listar_turmas_pap(
            ano_letivo=anoLetivo, codigo_escola=codigoEscola
        )
        return Response(TurmaPapResumoSerializer(data, many=True).data)


class VerificarSeAlunosSaoTurmaProgramaPapView(APIView):
    """Verifica se alunos pertencem a turmas PAP"""

    @extend_schema(
        tags=_TAG,
        description=(
            "Verifica se alunos pertencem a turmas PAP"
        ),
        parameters=[
            OpenApiParameter(
                "codigosAlunos",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
            ),
        ],
        responses={200: AlunoTurmaProgramaPapSerializer(many=True)},
    )
    def get(self, request: Request, anoLetivo: int) -> Response:
        codigos_alunos = request.query_params.getlist("codigosAlunos")
        if not codigos_alunos:
            return detail_response(
                "E necessario informar ao menos um codigosAlunos."
            )

        data = services.verificar_alunos_pap(
            ano_letivo=anoLetivo, codigos_alunos=codigos_alunos
        )
        return Response(
            AlunoTurmaProgramaPapSerializer(data, many=True).data
        )


class ObterAlunosPapAnoCorrenteView(APIView):
    """Lista alunos PAP do ano corrente"""

    @extend_schema(
        tags=_TAG,
        description=(
            "Lista alunos PAP do ano corrente"
        ),
        responses={200: AlunoTurmaPapSerializer(many=True)},
    )
    def get(self, _request: Request) -> Response:
        data = services.listar_alunos_pap_ano_corrente()
        return Response(AlunoTurmaPapSerializer(data, many=True).data)


class ObterAlunosPapPorAnoLetivoView(APIView):
    """Lista alunos PAP por ano letivo"""

    @extend_schema(
        tags=_TAG,
        description=(
            "Lista alunos PAP por ano letivo"
        ),
        responses={200: AlunoTurmaPapSerializer(many=True)},
    )
    def get(self, _request: Request, anoLetivo: int) -> Response:
        data = services.listar_alunos_pap_por_ano(ano_letivo=anoLetivo)
        return Response(AlunoTurmaPapSerializer(data, many=True).data)
