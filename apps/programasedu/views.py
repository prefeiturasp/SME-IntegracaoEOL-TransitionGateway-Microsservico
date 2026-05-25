"""Views do domínio de programas educacionais."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.core.responses import Response, detail_response
from apps.programasedu import services
from apps.programasedu.serializers import (
    AlunoTurmaPapSerializer,
    AlunoTurmaProgramaPapSerializer,
    ComponenteTurmaProgramaAlunoSerializer,
    DadosSrmPaeeColaborativoSerializer,
    TurmaPapResumoSerializer,
)

_TAG = ["Aluno"]


class ObterTurmasPapView(APIView):
    """Lista turmas PAP por ano letivo e UE."""

    @extend_schema(
        tags=_TAG,
        summary="Turmas PAP por ano letivo e UE",
        description=(
            "Retorna as turmas PAP (Programa de Apoio Pedagógico) "
            "vinculadas à UE no ano letivo informado."
        ),
        parameters=[
            OpenApiParameter(
                "ano_letivo",
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                required=True,
                description="Ano letivo das turmas PAP.",
            ),
            OpenApiParameter(
                "codigo_escola",
                OpenApiTypes.STR,
                OpenApiParameter.PATH,
                required=True,
                description="Código EOL da escola (UE).",
            ),
        ],
        responses={200: TurmaPapResumoSerializer(many=True)},
    )
    def get(
        self, _request: Request, ano_letivo: int, codigo_escola: str
    ) -> Response:
        """ Verifica a resposta de turmas PAP por ano letivo e UE."""
        if not codigo_escola.strip():
            return detail_response("É necessário informar o codigo_escola.")
        data = services.listar_turmas_pap(
            ano_letivo=ano_letivo, codigo_escola=codigo_escola
        )
        return Response(TurmaPapResumoSerializer(data, many=True).data)


class VerificarSeAlunosSaoTurmaProgramaPapView(APIView):
    """Verifica se alunos pertencem a turmas PAP."""

    @extend_schema(
        tags=_TAG,
        summary="Verificar se alunos pertencem a turmas PAP",
        description=(
            "Dada uma lista de códigos de alunos, retorna apenas os que "
            "estão vinculados a turmas PAP no ano letivo informado."
        ),
        parameters=[
            OpenApiParameter(
                "ano_letivo",
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                required=True,
                description="Ano letivo de referência.",
            ),
            OpenApiParameter(
                "codigos_alunos",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
                description="Lista de códigos EOL de alunos.",
            ),
        ],
        responses={200: AlunoTurmaProgramaPapSerializer(many=True)},
    )
    def get(self, request: Request, ano_letivo: int) -> Response:
        """ Verifica a resposta de verificação de alunos em turmas PAP."""
        codigos_alunos = request.query_params.getlist("codigos_alunos")
        if not codigos_alunos:
            return detail_response(
                "É necessário informar ao menos um codigos_alunos."
            )

        data = services.verificar_alunos_pap(
            ano_letivo=ano_letivo, codigos_alunos=codigos_alunos
        )
        return Response(AlunoTurmaProgramaPapSerializer(data, many=True).data)


class ObterAlunosPapAnoCorrenteView(APIView):
    """Lista alunos PAP do ano corrente."""

    @extend_schema(
        tags=_TAG,
        summary="Alunos PAP do ano corrente",
        description=(
            "Retorna todos os alunos vinculados a turmas PAP no ano "
            "letivo corrente."
        ),
        responses={200: AlunoTurmaPapSerializer(many=True)},
    )
    def get(self, _request: Request) -> Response:
        """ Verifica a resposta de alunos PAP do ano corrente."""
        data = services.listar_alunos_pap_ano_corrente()
        return Response(AlunoTurmaPapSerializer(data, many=True).data)


class ObterAlunosPapPorAnoLetivoView(APIView):
    """Lista alunos PAP por ano letivo."""

    @extend_schema(
        tags=_TAG,
        summary="Alunos PAP por ano letivo",
        description=(
            "Retorna todos os alunos vinculados a turmas PAP no ano "
            "letivo informado."
        ),
        parameters=[
            OpenApiParameter(
                "ano_letivo",
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                required=True,
                description="Ano letivo de referência.",
            ),
        ],
        responses={200: AlunoTurmaPapSerializer(many=True)},
    )
    def get(self, _request: Request, ano_letivo: int) -> Response:
        """ Verifica a resposta de alunos PAP por ano letivo."""
        data = services.listar_alunos_pap_por_ano(ano_letivo=ano_letivo)
        return Response(AlunoTurmaPapSerializer(data, many=True).data)


class ObterComponentesCurricularesTurmasProgramaAlunoView(APIView):
    """Lista componentes curriculares das turmas de programa do aluno."""

    @extend_schema(
        tags=_TAG,
        summary="Componentes das turmas de programa do aluno",
        description=(
            "Retorna os componentes curriculares das turmas de programa "
            "em que o aluno está matriculado no ano letivo informado."
        ),
        parameters=[
            OpenApiParameter(
                "codigo_aluno",
                OpenApiTypes.STR,
                OpenApiParameter.PATH,
                required=True,
                description="Código EOL do aluno.",
            ),
            OpenApiParameter(
                "ano_letivo",
                OpenApiTypes.INT,
                OpenApiParameter.PATH,
                required=True,
                description="Ano letivo de referência.",
            ),
        ],
        responses={200: ComponenteTurmaProgramaAlunoSerializer(many=True)},
    )
    def get(
        self, _request: Request, codigo_aluno: str, ano_letivo: int
    ) -> Response:
        """ Verifica a resposta de componentes curriculares das turmas de programa do aluno."""
        if not codigo_aluno.strip():
            return detail_response("É necessário informar o codigo_aluno.")
        data = services.listar_componentes_turmas_programa_aluno(
            codigo_aluno=codigo_aluno, ano_letivo=ano_letivo
        )
        return Response(
            ComponenteTurmaProgramaAlunoSerializer(data, many=True).data
        )


class ObterDadosSrmPaeeAlunoView(APIView):
    """Retorna dados de SRM/PAEE colaborativo do aluno."""

    @extend_schema(
        tags=_TAG,
        summary="Dados de SRM/PAEE colaborativo do aluno",
        description=(
            "Retorna os dados de SRM/PAEE colaborativo do aluno informado."
        ),
        parameters=[
            OpenApiParameter(
                "codigo_aluno",
                OpenApiTypes.STR,
                OpenApiParameter.PATH,
                required=True,
                description="Código EOL do aluno.",
            ),
        ],
        responses={200: DadosSrmPaeeColaborativoSerializer(many=True)},
    )
    def get(self, _request: Request, codigo_aluno: str) -> Response:
        """ Verifica a resposta de dados de SRM/PAEE colaborativo do aluno."""
        if not codigo_aluno.strip():
            return detail_response("E necessario informar o codigo_aluno.")
        data = services.obter_dados_srm_paee_aluno(codigo_aluno=codigo_aluno)
        return Response(
            DadosSrmPaeeColaborativoSerializer(data, many=True).data
        )
