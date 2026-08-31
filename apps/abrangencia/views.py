"""Views do domínio de abrangência (estrutura institucional vigente)."""

from typing import Any

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.abrangencia import services
from apps.abrangencia.serializers import EstruturaVigenteSerializer
from apps.core.views import DomainAPIView

_TAG = ["Abrangencia"]
_DOMINIO_PEDAGOGICO = "pedagogico"
_MSG_CODIGO_DRE_OBRIGATORIO = "O codigo da Dre é obrigatório"
_MSG_FILTRO_TURMAS_OBRIGATORIO = "É necessário informar ao menos uma turma"


class AbrangenciaAPIView(DomainAPIView):
    """APIView base que padroniza falhas de comunicação com pedagógico."""

    api_domain = _DOMINIO_PEDAGOGICO


def _filtrar_codigos_turma(data: Any) -> list[int]:
    """Extrai códigos de turma válidos do corpo da requisição.

    Args:
        data: Corpo da requisição.

    Returns:
        Códigos numéricos informados, ignorando itens não numéricos.
    """
    if not isinstance(data, list):
        return []
    return [
        int(item) for item in data if str(item).strip().lstrip("-").isdigit()
    ]


class EstruturaVigentePorDreView(AbrangenciaAPIView):
    """Retorna a estrutura institucional vigente de uma DRE."""

    @extend_schema(
        tags=_TAG,
        summary="Estrutura institucional vigente de uma DRE",
        description=(
            "Retorna a árvore DRE→UE→turma vigente para a DRE informada.\n\n"
            "Contrato: `GET /api/abrangencia/estrutura-vigente/{codigoDre}`."
        ),
        parameters=[
            OpenApiParameter(
                name="codigo_dre",
                location=OpenApiParameter.PATH,
                description="Código EOL da DRE",
                required=True,
                type=str,
            )
        ],
        responses={
            200: EstruturaVigenteSerializer,
            204: None,
            400: None,
        },
    )
    def get(self, _request: Request, codigo_dre: str) -> Response:
        """Retorna a estrutura institucional vigente da DRE.

        Args:
            _request: Requisição HTTP recebida.
            codigo_dre: Código EOL da DRE.

        Returns:
            Estrutura DRE→UE→turma, 204 quando vazia, ou 400 quando o
            código da DRE não é informado.
        """
        if not codigo_dre.strip():
            return Response(
                {"detail": _MSG_CODIGO_DRE_OBRIGATORIO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = services.get_estrutura_vigente_por_dre(codigo_dre.strip())
        if not data.get("dres"):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(EstruturaVigenteSerializer(data).data)


class EstruturaVigenteView(AbrangenciaAPIView):
    """Retorna a estrutura institucional vigente de uma lista de turmas."""

    @extend_schema(
        tags=_TAG,
        summary="Estrutura institucional vigente por lista de turmas",
        description=(
            "Retorna a árvore DRE→UE→turma vigente para os códigos de "
            "turma informados no corpo da requisição (`filtroTurmas`).\n\n"
            "Contrato: `POST /api/abrangencia/estrutura-vigente`."
        ),
        request={
            "application/json": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        responses={
            200: EstruturaVigenteSerializer,
            204: None,
            400: None,
        },
    )
    def post(self, request: Request) -> Response:
        """Retorna a estrutura institucional vigente das turmas informadas.

        Args:
            request: Requisição HTTP com a lista de códigos de turma
                (``filtroTurmas``) no corpo.

        Returns:
            Estrutura DRE→UE→turma, 204 quando vazia, ou 400 quando a lista
            de turmas não é informada.
        """
        codigos = _filtrar_codigos_turma(request.data)
        if not codigos:
            return Response(
                {"detail": _MSG_FILTRO_TURMAS_OBRIGATORIO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = services.get_estrutura_vigente_por_turmas(codigos)
        if not data.get("dres"):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(EstruturaVigenteSerializer(data).data)
