import httpx
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.institucional import services
from apps.institucional.serializers import (
    DRESerializer,
    EscolaResumoSerializer,
    EscolaSerializer,
    EquipamentoSerializer,
)

_TAG_DRE = ["DiretoriaRegionalEducacao"]
_TAG_ESCOLA = ["Escola"]

# Sidecar retorna campos extras; filtramos para o contrato D05/D06.
_ESCOLA_RESUMO_CAMPOS = {
    "codigoEscola",
    "nomeEscola",
    "codigoDRE",
    "tipoEscola",
    "siglaTipoEscola",
    "nomeDRE",
    "siglaDRE",
    "codigoSubprefeitura",
    "nomeSubprefeitura",
}

# Campos do contrato E02 da API EOL.
_ESCOLA_DETALHE_CAMPOS = {
    "codigoEscola",
    "nomeEscola",
    "nomeDRE",
    "siglaDRE",
    "codigoDRE",
    "tipoEscola",
    "siglaTipoEscola",
    "codigoTipoEscola",
}


def _filtrar_escola_resumo(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _ESCOLA_RESUMO_CAMPOS}


def _filtrar_escola_detalhe(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _ESCOLA_DETALHE_CAMPOS}


class DREListView(APIView):
    """D01 — Lista todas as DREs cadastradas no ETL institucional."""

    @extend_schema(
        tags=_TAG_DRE,
        summary="Lista todas as DREs",
        description=(
            "Retorna a lista completa de Diretorias Regionais de Educação "
            "sincronizadas pelo ETL institucional a partir do EOL.\n\n"
            "Contrato D01: `GET /api/DREs`."
        ),
        responses={200: DRESerializer(many=True)},
    )
    def get(self, _request: Request) -> Response:
        return Response(services.get_dres())


class DREDetalheView(APIView):
    """D04 — Retorna dados de uma DRE específica pelo codigoEolDRE."""

    @extend_schema(
        tags=_TAG_DRE,
        summary="Detalhe de uma DRE",
        description=(
            "Retorna dados completos da Diretoria Regional de Educação "
            "identificada pelo `codigoEolDRE`.\n\n"
            "Contrato D04: `GET /api/DREs/{codigoEolDRE}`."
        ),
        parameters=[
            OpenApiParameter(
                name="codigo_eol_dre",
                location=OpenApiParameter.PATH,
                description="Código EOL da DRE",
                required=True,
                type=str,
            )
        ],
        responses={200: DRESerializer(many=True), 404: None},
    )
    def get(self, _request: Request, codigo_eol_dre: str) -> Response:
        try:
            data = services.get_dre(codigo_eol_dre)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        if not data:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(data if isinstance(data, list) else [data])


class EscolasPorDREView(APIView):
    """D06 — Lista escolas vinculadas a uma DRE específica."""

    @extend_schema(
        tags=_TAG_DRE,
        summary="Escolas de uma DRE",
        description=(
            "Retorna lista das unidades educacionais vinculadas "
            "à Diretoria Regional de Educação informada.\n\n"
            "Contrato D06: `GET /api/DREs/{codigoEolDRE}/escola`."
        ),
        parameters=[
            OpenApiParameter(
                name="codigo_eol_dre",
                location=OpenApiParameter.PATH,
                description="Código EOL da DRE",
                required=True,
                type=str,
            )
        ],
        responses={200: EscolaResumoSerializer(many=True), 404: None},
    )
    def get(self, _request: Request, codigo_eol_dre: str) -> Response:
        try:
            data = services.get_escolas_por_dre(codigo_eol_dre)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        return Response([_filtrar_escola_resumo(e) for e in data])


class EscolasPorDREeTipoView(APIView):
    """D05 — Lista escolas de uma DRE filtradas por tipo de escola."""

    @extend_schema(
        tags=_TAG_DRE,
        summary="Escolas de uma DRE por tipo",
        description=(
            "Retorna lista de unidades educacionais vinculadas à DRE "
            "filtradas pelo tipo de escola informado.\n\n"
            "Contrato D05: `GET /api/DREs/{codigoEolDRE}/escolas/{tipoEscola}`."
        ),
        parameters=[
            OpenApiParameter(
                name="codigo_eol_dre",
                location=OpenApiParameter.PATH,
                description="Código EOL da DRE",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="tipo_escola",
                location=OpenApiParameter.PATH,
                description="Código do tipo de escola",
                required=True,
                type=str,
            ),
        ],
        responses={200: EscolaResumoSerializer(many=True), 404: None},
    )
    def get(
        self, _request: Request, codigo_eol_dre: str, tipo_escola: str
    ) -> Response:
        try:
            data = services.get_escolas_por_dre_e_tipo(
                codigo_eol_dre, tipo_escola
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        return Response([_filtrar_escola_resumo(e) for e in data])


class EscolaDetalheView(APIView):
    """E02 — Retorna dados de uma escola pelo codigoEscolaEol."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Detalhe de uma escola",
        description=(
            "Retorna dados da unidade educacional identificada "
            "pelo `codigoEscolaEol`.\n\n"
            "Contrato E02: `GET /api/escolas/{codigoEscolaEol}`."
        ),
        parameters=[
            OpenApiParameter(
                name="codigo_escola_eol",
                location=OpenApiParameter.PATH,
                description="Código EOL da escola",
                required=True,
                type=str,
            )
        ],
        responses={200: EscolaSerializer, 404: None},
    )
    def get(self, _request: Request, codigo_escola_eol: str) -> Response:
        try:
            data = services.get_escola(codigo_escola_eol)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        # Sidecar retorna array — extrai o primeiro item e filtra para o contrato E02.
        item = data[0] if isinstance(data, list) and data else data
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(_filtrar_escola_detalhe(item))


_EQUIPAMENTOS_PARAMS = [
    OpenApiParameter("codigosSubprefeitura", int, many=True, required=False, description="Lista de códigos de subprefeituras"),
    OpenApiParameter("codigosDre", int, many=True, required=False, description="Lista de códigos de DREs"),
    OpenApiParameter("tiposUnidade", int, many=True, required=False, description="Lista de códigos de tipo unidade educação"),
    OpenApiParameter("tiposEscola", int, many=True, required=False, description="Lista de códigos de tipo escola"),
    OpenApiParameter("nomeEscola", str, required=False, description="Nome da UE"),
    OpenApiParameter("codigoEol", str, required=False, description="Código EOL da UE"),
]


class EquipamentosView(APIView):
    """E25 — Lista equipamentos das unidades educacionais com filtros opcionais."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Equipamentos das escolas",
        description=(
            "Retorna lista de equipamentos cadastrados nas unidades "
            "educacionais. Todos os filtros são opcionais; sem nenhum o "
            "sidecar executa query irrestrita e pode gerar timeout.\n\n"
            "Contrato E25: `GET /api/escolas/equipamentos`."
        ),
        parameters=_EQUIPAMENTOS_PARAMS,
        responses={200: EquipamentoSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        qp = request.query_params
        data = services.get_equipamentos(
            codigos_subprefeitura=qp.getlist("codigosSubprefeitura") or None,
            codigos_dre=qp.getlist("codigosDre") or None,
            tipos_unidade=qp.getlist("tiposUnidade") or None,
            tipos_escola=qp.getlist("tiposEscola") or None,
            nome_escola=qp.get("nomeEscola"),
            codigo_eol=qp.get("codigoEol"),
        )
        serializer = EquipamentoSerializer(data, many=True)
        return Response(serializer.data)
