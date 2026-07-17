"""Views do domínio institucional."""

from typing import Any, cast

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
    EscolaSigpaeSerializer,
    EscolaPorDreETipoSerializer,
    EscolaResumoSerializer,
    EscolaSerializer,
    SincronizacaoInstitucionalSerializer,
    SubprefeiturasSerializer,
    TipoEscolaSerializer,
    UnidadeCodigoIntegracaoSerializer,
    UnidadeEducacionalSerializer,
    UnidadeEolSerializer,
    UnidadeParceiraSerializer,
)

_TAG_DRE = ["DiretoriaRegionalEducacao"]
_TAG_ESCOLA = ["Escola"]
_SIDECAR_INDISPONIVEL_DETAIL = "Serviço institucional indisponível"

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

_ESCOLA_SIGPAE_CAMPOS = {
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

_UNIDADE_CODIGO_INTEGRACAO_CAMPOS = {
    "codigoUe",
    "nomeUe",
    "codigoIntegracao",
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

_TODA_UNIDADE_CAMPOS = {
    "codigoEscola",
    "nomeEscola",
    "nomeDRE",
    "siglaDRE",
    "codigoDRE",
    "tipoEscola",
    "siglaTipoEscola",
}

_SINCRONIZACAO_INSTITUCIONAL_CAMPOS = {
    "ueCodigo",
    "dataAtualizacao",
    "dreCodigo",
    "ueNome",
    "tipoEscolaCodigo",
}


def _filtrar_escola_resumo(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _ESCOLA_RESUMO_CAMPOS}


def _filtrar_escola_detalhe(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _ESCOLA_DETALHE_CAMPOS}


def _filtrar_escola_por_dre_tipo(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _ESCOLA_POR_DRE_TIPO_CAMPOS}


def _filtrar_escola_sigpae(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _ESCOLA_SIGPAE_CAMPOS}


def _filtrar_unidade_codigo_integracao(item: dict) -> dict:
    return {
        k: v
        for k, v in item.items()
        if k in _UNIDADE_CODIGO_INTEGRACAO_CAMPOS
    }


def _filtrar_dados_escola(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _DADOS_ESCOLA_CAMPOS}


def _filtrar_toda_unidade(item: dict) -> dict:
    return {k: v for k, v in item.items() if k in _TODA_UNIDADE_CAMPOS}


def _filtrar_sincronizacao_institucional(item: dict) -> dict:
    return {
        k: v
        for k, v in item.items()
        if k in _SINCRONIZACAO_INSTITUCIONAL_CAMPOS
    }


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


class EscolasSigpaePorDREView(APIView):
    """Lista escolas de uma DRE no formato SIGPAE."""

    @extend_schema(
        tags=_TAG_DRE,
        summary="Escolas SIGPAE de uma DRE",
        description=(
            "Retorna lista de unidades educacionais de uma DRE "
            "no formato esperado pelo SIGPAE.\n\n"
            "Contrato D09: `GET /api/dres/{codigoEolDRE}/escola/Sigpae/`."
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
        responses={
            200: EscolaSigpaeSerializer(many=True),
            404: None,
        },
    )
    def get(self, _request: Request, codigo_eol_dre: str) -> Response:
        """Retorna escolas SIGPAE por DRE."""
        try:
            data = services.get_escolas_sigpae_por_dre(codigo_eol_dre)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        except httpx.RequestError:
            return _sidecar_unavailable_response()

        if not data:
            return Response([])
        if isinstance(data, list):
            return Response([
                _filtrar_escola_sigpae(item)
                for item in data
                if isinstance(item, dict)
            ])
        if isinstance(data, dict):
            return Response([_filtrar_escola_sigpae(data)])
        return Response([])


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


class UnidadeCodigoIntegracaoPorDREView(APIView):
    """Lista UEs com código de integração por DRE."""

    @extend_schema(
        tags=_TAG_DRE,
        summary="UEs com código de integração por DRE",
        description=(
            "Retorna lista de unidades educacionais da DRE com seus "
            "códigos de integração.\n\n"
            "Contrato D11: "
            "`GET /api/dres/{dreCodigo}/unidades/codigo-integracao/`."
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
        responses={200: UnidadeCodigoIntegracaoSerializer(many=True), 404: None},
    )
    def get(self, _request: Request, dre_codigo: str) -> Response:
        """Retorna UEs com código de integração da DRE."""
        try:
            data = services.get_unidades_codigo_integracao_por_dre(dre_codigo)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        except httpx.RequestError:
            return _sidecar_unavailable_response()
        if not data:
            return Response([])
        if isinstance(data, list):
            return Response([
                _filtrar_unidade_codigo_integracao(item)
                for item in data
                if isinstance(item, dict)
            ])
        if isinstance(data, dict):
            return Response([_filtrar_unidade_codigo_integracao(data)])
        return Response([])


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


class SubprefeiturasPorEscolaView(APIView):
    """Lista subprefeituras vinculadas à escola."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Subprefeituras da escola",
        description=(
            "Retorna subprefeituras vinculadas à unidade educacional.\n\n"
            "Contrato E17: "
            "`GET /api/escolas/{codigoEscolaEol}/subprefeituras/`."
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
        responses={200: SubprefeiturasSerializer(many=True), 404: None},
    )
    def get(self, _request: Request, codigo_escola_eol: str) -> Response:
        """Retorna subprefeituras da escola."""
        try:
            data = services.get_subprefeituras_por_escola(codigo_escola_eol)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return Response(status=status.HTTP_404_NOT_FOUND)
            raise
        except httpx.RequestError:
            return _sidecar_unavailable_response()
        return Response(data)


def _sidecar_error_response(exc: httpx.HTTPStatusError) -> Response:
    """Converte erro HTTP do sidecar em resposta do gateway."""

    try:
        body: Any = exc.response.json()
    except ValueError:
        detail = exc.response.text.strip() or exc.response.reason_phrase
        body = {"detail": detail}
    return Response(body, status=exc.response.status_code)


def _sidecar_unavailable_response() -> Response:
    """Resposta padrão quando o sidecar institucional não responde."""

    return Response(
        {"detail": _SIDECAR_INDISPONIVEL_DETAIL},
        status=status.HTTP_502_BAD_GATEWAY,
    )


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


class EscolasListPostView(APIView):
    """Lista escolas pelos códigos informados no corpo da requisição."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Escolas por lista de códigos",
        description=(
            "Retorna escolas correspondentes aos códigos EOL informados no "
            "corpo da requisição."
        ),
        request={
            "application/json": {"type": "array", "items": {"type": "string"}}
        },
        responses={200: UnidadeEducacionalSerializer(many=True), 400: None},
    )
    def post(self, request: Request) -> Response:
        """Retorna escolas encontradas para os códigos informados."""

        try:
            codigos = cast(list[str], request.data)
            data = services.post_escolas(codigos)
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError:
            return _sidecar_unavailable_response()

        if not data:
            return Response([])
        if isinstance(data, list):
            return Response([
                _filtrar_toda_unidade(item)
                for item in data
                if isinstance(item, dict)
            ])
        if isinstance(data, dict):
            resultados = data.get("results")
            if isinstance(resultados, list):
                return Response([
                    _filtrar_toda_unidade(item)
                    for item in resultados
                    if isinstance(item, dict)
                ])
        return Response([])


class EscolaDetalheView(APIView):
    """Retorna dados de uma escola."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Detalhe de uma escola",
        description=(
            "Retorna dados da unidade educacional identificada pelo `codigoEscolaEol`."
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


class UnidadeEolView(APIView):
    """Retorna dados resumidos de uma unidade pelo código EOL."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Unidade por código EOL",
        description=(
            "Retorna os dados resumidos da unidade educacional identificada pelo `codigoEol`"
        ),
        parameters=[
            OpenApiParameter(
                name="codigo_eol",
                location=OpenApiParameter.PATH,
                description="Código EOL da unidade educacional",
                required=True,
                type=str,
            )
        ],
        responses={200: UnidadeEolSerializer, 204: None},
    )
    def get(self, _request: Request, codigo_eol: str) -> Response:
        """Retorna dados resumidos da unidade por código EOL."""

        try:
            data = services.get_unidade_eol(codigo_eol)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return _sidecar_error_response(exc)
        except httpx.RequestError:
            return _sidecar_unavailable_response()

        if not data:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data)


class SincronizacoesInstitucionaisView(APIView):
    """Retorna a sincronização institucional de uma UE."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Sincronizações institucionais da escola",
        description=(
            "Retorna os dados de sincronização institucional da unidade "
            "educacional identificada pelo `ueCodigo`.\n\n"
            "Contrato E23: "
            "`GET /api/escolas/{ueCodigo}/sincronizacoes-institucionais/`."
        ),
        parameters=[
            OpenApiParameter(
                name="ue_codigo",
                location=OpenApiParameter.PATH,
                description="Código EOL da unidade educacional",
                required=True,
                type=str,
            )
        ],
        responses={200: SincronizacaoInstitucionalSerializer, 204: None},
    )
    def get(self, _request: Request, ue_codigo: str) -> Response:
        """Retorna sincronização institucional ou 204 quando ausente."""

        try:
            data = services.get_sincronizacoes_institucionais(ue_codigo)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return _sidecar_error_response(exc)
        except httpx.RequestError:
            return _sidecar_unavailable_response()

        if not data:
            return Response(status=status.HTTP_204_NO_CONTENT)
        if isinstance(data, dict):
            return Response(_filtrar_sincronizacao_institucional(data))
        return Response(data)


class UnidadesParceirasView(APIView):
    """Retorna unidades parceiras pelos códigos informados."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Unidades parceiras",
        description=(
            "Retorna a lista de unidades parceiras informadas no corpo da requisição."
        ),
        request={
            "application/json": {"type": "array", "items": {"type": "string"}}
        },
        responses={200: UnidadeParceiraSerializer(many=True), 400: None},
    )
    def post(self, request: Request) -> Response:
        """Retorna unidades parceiras compatíveis com o legado."""

        try:
            codigos = cast(list[str], request.data)
            data = services.post_unidades_parceiras(codigos)
        except httpx.HTTPStatusError as exc:
            return _sidecar_error_response(exc)
        except httpx.RequestError:
            return _sidecar_unavailable_response()

        return Response(data or [])


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
            "cadastradas no sistema."
        ),
        responses={200: UnidadeEducacionalSerializer(many=True)},
    )
    def get(self, _request: Request) -> Response:
        try:
            data = services.get_todas_unidades()
        except httpx.RequestError:
            return Response(
                {"detail": _SIDECAR_INDISPONIVEL_DETAIL},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        resultados = data.get("results") if isinstance(data, dict) else data
        if not resultados:
            return Response([])
        return Response([
            _filtrar_toda_unidade(item) for item in resultados if isinstance(item, dict)
        ])


class TiposUnidadeEducacaoView(APIView):
    """Lista tipos de unidade educacional."""

    @extend_schema(
        tags=_TAG_ESCOLA,
        summary="Tipos de unidade educacional",
        description=(
            "Retorna lista de tipos de unidade educacional cadastrados "
            "no sistema."
        ),
    )
    def get(self, _request: Request) -> Response:
        try:
            data = services.get_tipos_unidade_educacao()
        except httpx.RequestError:
            return Response(
                {"detail": _SIDECAR_INDISPONIVEL_DETAIL},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(data)
