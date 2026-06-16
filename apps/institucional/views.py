"""Views do domínio institucional."""

from typing import cast

import httpx
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.institucional import services
from apps.institucional.serializers import (
    DadosEscolaSerializer,
    DRESerializer,
    EquipamentoSerializer,
    EscolaPorDreETipoSerializer,
    EscolaResumoSerializer,
    EscolaSerializer,
    SubprefeiturasSerializer,
    TipoEscolaSerializer,
)

_TAG_DRE = ["DiretoriaRegionalEducacao"]
_TAG_ESCOLA = ["Escola"]

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

_ESCOLA_POR_DRE_TIPO_CAMPOS = {
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

_DADOS_ESCOLA_CAMPOS = {
    "nomeDRE",
    "siglaDRE",
    "codigoDRE",
    "codigoINEP",
    "siglaTipoEscola",
    "nome",
    "nomeExibicao",
    "codigo",
    "tipoUnidade",
    "email",
    "telefone",
    "tipoLogradouro",
    "logradouro",
    "numero",
    "bairro",
    "cep",
    "municipio",
    "uf",
    "tipoUnidadeAdm",
    "descTipoUnidadeAdm",
}


def _filtrar_escola_resumo(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _ESCOLA_RESUMO_CAMPOS}


def _filtrar_escola_detalhe(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _ESCOLA_DETALHE_CAMPOS}


def _filtrar_escola_por_dre_tipo(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _ESCOLA_POR_DRE_TIPO_CAMPOS}


def _filtrar_dados_escola(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _DADOS_ESCOLA_CAMPOS}


class DREListView(APIView):
    """Lista Diretorias Regionais de Educação."""

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

    @extend_schema(
        tags=_TAG_DRE,
        summary="Filtra DREs por lista de códigos",
        description=(
            "Retorna Diretorias Regionais de Educação correspondentes "
            "à lista de códigos EOL informada no corpo da requisição.\n\n"
            "Contrato D02: `POST /api/DREs`."
        ),
        request=DRESerializer(many=True),
        responses={200: DRESerializer(many=True), 204: None},
    )
    def post(self, request: Request) -> Response:
        codigos = cast(list[str], request.data)
        data = services.get_dres_por_codigos(codigos)
        if not data:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data)


class DREDetalheView(APIView):
    """Retorna dados de uma Diretoria Regional de Educação."""

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
    """Lista escolas vinculadas a uma DRE."""

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


class SubprefeiturasPorDREView(APIView):
    """Lista subprefeituras vinculadas à DRE."""

    @extend_schema(
        tags=_TAG_DRE,
        summary="Subprefeituras de uma DRE",
        description=(
            "Retorna lista de subprefeituras vinculadas à Diretoria "
            "Regional de Educação informada.\n\n"
            "Contrato D07: `GET /api/DREs/{dreCodigo}/subprefeituras`."
        ),
        parameters=[
            OpenApiParameter(
                name="dre_codigo",
                location=OpenApiParameter.PATH,
                description="Código da DRE",
                required=True,
                type=str,
            )
        ],
        responses={200: SubprefeiturasSerializer(many=True), 404: None},
    )
    def get(self, _request: Request, dre_codigo: str) -> Response:
        try:
            data = services.get_subprefeituras_por_dre(dre_codigo)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        return Response(data)


class EscolasPorDREeTipoView(APIView):
    """Lista escolas de uma DRE por tipo."""

    @extend_schema(
        tags=_TAG_DRE,
        summary="Escolas de uma DRE por tipo",
        description=(
            "Retorna lista de unidades educacionais vinculadas à DRE "
            "filtradas pelo tipo de escola informado.\n\n"
            "Contrato D05: "
            "`GET /api/DREs/{codigoEolDRE}/escolas/{tipoEscola}`."
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
        responses={200: EscolaPorDreETipoSerializer(many=True), 404: None},
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
        return Response([_filtrar_escola_por_dre_tipo(e) for e in data])


class UesPorDREView(APIView):
    """Lista códigos de UEs vinculadas à DRE."""

    @extend_schema(
        tags=_TAG_DRE,
        summary="Códigos de UEs de uma DRE",
        description=(
            "Retorna lista de códigos de unidades educacionais vinculadas "
            "à Diretoria Regional de Educação informada.\n\n"
            "Contrato D08: `GET /api/DREs/{dreCodigo}/ues`."
        ),
        parameters=[
            OpenApiParameter(
                name="dre_codigo",
                location=OpenApiParameter.PATH,
                description="Código da DRE",
                required=True,
                type=str,
            )
        ],
        responses={200: None, 404: None},
    )
    def get(self, _request: Request, dre_codigo: str) -> Response:
        try:
            data = services.get_ues_por_dre(dre_codigo)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        return Response(data)


class UnidadesPorDREView(APIView):
    """Lista unidades administrativas vinculadas à DRE."""

    @extend_schema(
        tags=_TAG_DRE,
        summary="Unidades de uma DRE",
        description=(
            "Retorna lista completa de unidades administrativas vinculadas "
            "à Diretoria Regional de Educação informada.\n\n"
            "Contrato D10: `GET /api/DREs/{dreCodigo}/unidades`."
        ),
        parameters=[
            OpenApiParameter(
                name="dre_codigo",
                location=OpenApiParameter.PATH,
                description="Código da DRE",
                required=True,
                type=str,
            )
        ],
        responses={200: None, 404: None},
    )
    def get(self, _request: Request, dre_codigo: str) -> Response:
        try:
            data = services.get_unidades_por_dre(dre_codigo)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        return Response(data)


class DadosEscolaView(APIView):
    """Retorna dados completos de uma escola."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Dados completos de uma escola",
        description=(
            "Retorna dados completos da unidade educacional identificada "
            "pelo `codigoEscolaEol`.\n\n"
            "Contrato E04: `GET /api/escolas/dados/{codigoEscolaEol}`."
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
        responses={200: DadosEscolaSerializer, 404: None},
    )
    def get(self, _request: Request, codigo_escola_eol: str) -> Response:
        try:
            data = services.get_dados_escola(codigo_escola_eol)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        if not data:
            return Response(status=status.HTTP_404_NOT_FOUND)
        item = data[0] if isinstance(data, list) and data else data
        if isinstance(item, dict):
            return Response(_filtrar_dados_escola(item))
        return Response(item)


class TiposEscolasView(APIView):
    """Lista tipos de escola cadastrados."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Tipos de escola",
        description=(
            "Retorna lista de tipos de escola cadastrados.\n\n"
            "Contrato E11: `GET /api/escolas/tiposEscolas`."
        ),
        responses={200: TipoEscolaSerializer(many=True)},
    )
    def get(self, _request: Request) -> Response:
        return Response(services.get_tipos_escolas())


class EscolaDetalheView(APIView):
    """Retorna dados de uma escola."""

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
        # Sidecar retorna array; extrai o primeiro item para o contrato E02.
        item = data[0] if isinstance(data, list) and data else data
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(_filtrar_escola_detalhe(item))


_EQUIPAMENTOS_PARAMS = [
    OpenApiParameter(
        "codigosSubprefeitura",
        int,
        many=True,
        required=False,
        description="Lista de códigos de subprefeituras",
    ),
    OpenApiParameter(
        "codigosDre",
        int,
        many=True,
        required=False,
        description="Lista de códigos de DREs",
    ),
    OpenApiParameter(
        "tiposUnidade",
        int,
        many=True,
        required=False,
        description="Lista de códigos de tipo unidade educação",
    ),
    OpenApiParameter(
        "tiposEscola",
        int,
        many=True,
        required=False,
        description="Lista de códigos de tipo escola",
    ),
    OpenApiParameter(
        "nomeEscola", str, required=False, description="Nome da UE"
    ),
    OpenApiParameter(
        "codigoEol", str, required=False, description="Código EOL da UE"
    ),
]


class EquipamentosView(APIView):
    """Lista equipamentos das unidades educacionais."""

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


class TodasUnidadesView(APIView):
    """Lista todas as unidades educacionais."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Todas as unidades educacionais",
        description=(
            "Retorna lista completa de todas as unidades educacionais "
            "cadastradas no sistema.\n\n"
            "Contrato E27: `GET /api/escolas/todas-unidades`."
        ),
    )
    def get(self, _request: Request) -> Response:
        try:
            data = services.get_todas_unidades()
        except httpx.RequestError:
            return Response(
                {"detail": "Serviço institucional indisponível"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(data)


class TiposUnidadeEducacaoView(APIView):
    """Lista tipos de unidade educacional."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Tipos de unidade educacional",
        description=(
            "Retorna lista de tipos de unidade educacional cadastrados "
            "no sistema.\n\n"
            "Contrato E10: `GET /api/escolas/tipos_unidade_educacao`."
        ),
    )
    def get(self, _request: Request) -> Response:
        try:
            data = services.get_tipos_unidade_educacao()
        except httpx.RequestError:
            return Response(
                {"detail": "Serviço institucional indisponível"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(data)
