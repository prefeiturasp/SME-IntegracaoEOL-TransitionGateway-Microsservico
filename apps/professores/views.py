"""Views do domínio professores - contratos legados."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.core.responses import Response, detail_response
from apps.professores import services
from apps.professores.serializers import NomeServidorSerializer

_TAG_ACESSOS = ["Acessos"]
_TAG_FUNCIONARIO = ["Funcionario"]
_TAG_PROFESSOR = ["Professor"]


class ProfessorView(APIView):
    """Nome do professor pelo RF."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=(
            "Retorna o nome do professor correspondente ao RF informado."
        ),
        responses={200: OpenApiTypes.STR, 204: None},
    )
    def get(self, _request: Request, rf_professor: str) -> Response:
        if not rf_professor.strip():
            return detail_response("Codigo RF e obrigatorio.")
        data = services.get_professor(rf_professor)
        if data is None:
            return Response(status=204)
        return Response(data)


class ValidadeProfessorView(APIView):
    """Retorna booleano indicando se o professor é válido."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=("Retorna booleano indicando se o professor é válido."),
        responses={200: OpenApiTypes.BOOL},
    )
    def get(self, _request: Request, codigo_rf: str) -> Response:
        if not codigo_rf.strip():
            return detail_response("E necessario informar o codigoRF.")
        data = services.get_validade_professor(codigo_rf)
        return Response(data)


class FuncionarioAtivoView(APIView):
    """Retorna booleano indicando se o funcionário está ativo."""

    @extend_schema(
        tags=_TAG_ACESSOS,
        description=(
            "Retorna booleano indicando se o funcionário está ativo."
        ),
        responses={200: OpenApiTypes.BOOL},
    )
    def get(self, _request: Request, registro_funcional: str) -> Response:
        if not registro_funcional.strip():
            return detail_response(
                "E necessario informar o registro funcional."
            )
        data = services.get_funcionario_ativo(registro_funcional)
        return Response(data)


class NomeServidorView(APIView):
    """Retorna nome e CPF do servidor."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna nome e CPF do servidor."),
        responses={200: NomeServidorSerializer, 204: None},
    )
    def get(self, _request: Request, registro_funcional: str) -> Response:
        data = services.get_nome_servidor(registro_funcional)
        if data is None:
            return Response(status=204)
        return Response(NomeServidorSerializer(data).data)
