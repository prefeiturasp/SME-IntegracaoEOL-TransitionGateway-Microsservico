"""Views do domínio de professores."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.core.responses import Response, detail_response
from apps.professores import services
from apps.professores.serializers import (
    FuncionarioEscolaSerializer,
    ListaStringSerializer,
    NomeServidorSerializer,
    ProfessorBuscarPorRfSerializer,
    ProfessorTurmaSerializer,
    TurmasIdsSerializer,
)

_TAG_ACESSOS = ["Acessos"]
_TAG_ESCOLA = ["Escola"]
_TAG_FUNCIONARIO = ["Funcionario"]
_TAG_PROFESSOR = ["Professor"]

_MSG_CODIGO_RF_OBRIGATORIO = "E necessario informar o codigoRF."
_MSG_CODIGO_UE_OBRIGATORIO = "E necessario informar o codigoUE."
_MSG_REGISTRO_FUNCIONAL_OBRIGATORIO = (
    "E necessario informar o registro funcional."
)
_CAMPOS_TURMA = {
    "codigo_turma",
    "data_disponibilizacao_aulas",
    "data_atribuicao_aula",
}


def _parse_bool_param(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None


def _is_lista_turmas(data: object) -> bool:
    return isinstance(data, list) and all(
        isinstance(item, dict) and item.keys() >= _CAMPOS_TURMA
        for item in data
    )


class ProfessorView(APIView):
    """Retorna o nome do professor pelo RF."""

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
    """Retorna indicação de validade do professor."""

    @extend_schema(
        tags=_TAG_PROFESSOR,
        description=("Retorna booleano indicando se o professor é válido."),
        responses={200: OpenApiTypes.BOOL},
    )
    def get(self, _request: Request, codigo_rf: str) -> Response:
        if not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        data = services.get_validade_professor(codigo_rf)
        return Response(data)


class FuncionarioAtivoView(APIView):
    """Retorna indicação de atividade do funcionário."""

    @extend_schema(
        tags=_TAG_ACESSOS,
        description=(
            "Retorna booleano indicando se o funcionário está ativo."
        ),
        responses={200: OpenApiTypes.BOOL},
    )
    def get(self, _request: Request, registro_funcional: str) -> Response:
        if not registro_funcional.strip():
            return detail_response(_MSG_REGISTRO_FUNCIONAL_OBRIGATORIO)
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


class NomeUsuarioEolView(APIView):
    """Retorna nome de usuário EOL do funcionário."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna o nome de usuário EOL do funcionário."),
        responses={200: OpenApiTypes.STR, 204: None},
    )
    def get(self, _request: Request, registro_funcional: str) -> Response:
        if not registro_funcional.strip():
            return detail_response(_MSG_REGISTRO_FUNCIONAL_OBRIGATORIO)
        data = services.get_nome_usuario_eol(registro_funcional)
        if data is None:
            return Response(status=204)
        return Response(data)


class ProfessorBuscarPorRfView(APIView):
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


class FuncionariosBuscarPorListaRfView(APIView):
    """Retorna professores pelos RFs informados."""

    @extend_schema(
        tags=_TAG_FUNCIONARIO,
        description=("Retorna professores pelos RFs informados."),
        request=ListaStringSerializer,
        responses={200: ProfessorBuscarPorRfSerializer(many=True)},
    )
    def post(self, request: Request) -> Response:
        serializer = ListaStringSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = services.get_professores_por_lista_rf(serializer.validated_data)
        if data is None:
            return Response(status=204)
        return Response(ProfessorBuscarPorRfSerializer(data, many=True).data)


class EscolaFuncionariosCargoView(APIView):
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
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        if not codigo_cargo.strip():
            return detail_response("E necessario informar o codigoCargo.")
        data = services.get_funcionarios_escola_por_cargo(
            codigo_ue,
            codigo_cargo,
        )
        if data is None:
            return Response(status=204)
        return Response(FuncionarioEscolaSerializer(data, many=True).data)


class EscolaFuncionariosView(APIView):
    """Retorna funcionários vinculados à escola."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        description=("Retorna funcionários vinculados à escola."),
        responses={200: FuncionarioEscolaSerializer(many=True), 204: None},
    )
    def get(self, _request: Request, codigo_ue: str) -> Response:
        if not codigo_ue.strip():
            return detail_response(_MSG_CODIGO_UE_OBRIGATORIO)
        data = services.get_funcionarios_escola(codigo_ue)
        if data is None:
            return Response(status=204)
        return Response(FuncionarioEscolaSerializer(data, many=True).data)


class ProfessorDisciplinaTurmasView(APIView):
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
        if not codigo_rf.strip():
            return detail_response(_MSG_CODIGO_RF_OBRIGATORIO)
        if not disciplina_id.strip():
            return detail_response("E necessario informar a disciplina.")
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
            return detail_response(
                "Resposta invalida do sidecar de professores.",
                502,
            )
        return Response(ProfessorTurmaSerializer(data, many=True).data)
