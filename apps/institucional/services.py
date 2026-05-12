# Camada de serviço do domínio institucional no TransitionGateway.
# Integração realizada com o sidecar SME-IntegracaoEOL-Institucional-Microsservico
# via ServiceClient (apps/core/http_client.py), seguindo o mesmo padrão de
# apps/pedagogico/services.py e apps/professores/services.py.
# A URL base do sidecar é configurada em settings.SIDECAR_INSTITUCIONAL_URL
# e a chave de autenticação em SIDECAR_INSTITUCIONAL_API_KEY.

from typing import Any

from django.conf import settings

from apps.core.http_client import ServiceClient

_BASE = "/api/v1/institucional"

_client = ServiceClient(
    base_url=settings.SIDECAR_INSTITUCIONAL_URL,
    dominio="institucional",
    api_key=settings.SIDECAR_INSTITUCIONAL_API_KEY,
    api_key_header=settings.SIDECAR_INSTITUCIONAL_API_KEY_HEADER,
)


# EP-I1 → D01 do sidecar institucional
def get_dres() -> Any:
    """Retorna lista completa de DREs — contrato camelCase (D01)."""
    resp = _client.get(f"{_BASE}/dres/")
    resp.raise_for_status()
    return resp.json()


# EP-I2 → D04 do sidecar institucional (retorna array[1])
def get_dre(codigo_dre: str) -> Any:
    """Retorna array com uma DRE pelo código EOL — contrato camelCase (D04)."""
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/")
    resp.raise_for_status()
    return resp.json()


# EP-I3 → D06 do sidecar institucional
def get_escolas_por_dre(codigo_dre: str) -> Any:
    """Retorna escolas vinculadas a uma DRE — contrato camelCase (D06)."""
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/escola/")
    resp.raise_for_status()
    return resp.json()


# EP-I3b → D05 do sidecar institucional
def get_escolas_por_dre_e_tipo(codigo_dre: str, tipo_escola: str) -> Any:
    """Retorna escolas de uma DRE filtradas por tipo — contrato camelCase (D05)."""
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/escolas/{tipo_escola}/")
    resp.raise_for_status()
    return resp.json()


# EP-I4 → escolas/ do sidecar institucional
def get_escola(codigo_escola: str) -> Any:
    """Retorna dados de uma escola pelo código EOL — contrato camelCase."""
    resp = _client.get(f"{_BASE}/escolas/{codigo_escola}/")
    resp.raise_for_status()
    return resp.json()


# EP-I5 → escolas/equipamentos/ do sidecar institucional
def get_equipamentos(
    codigos_subprefeitura: list[str] | None = None,
    codigos_dre: list[str] | None = None,
    tipos_unidade: list[str] | None = None,
    tipos_escola: list[str] | None = None,
    nome_escola: str | None = None,
    codigo_eol: str | None = None,
) -> Any:
    """Retorna equipamentos das unidades educacionais — contrato camelCase."""
    params: dict[str, Any] = {}
    if codigos_subprefeitura:
        params["codigosSubprefeitura"] = codigos_subprefeitura
    if codigos_dre:
        params["codigosDre"] = codigos_dre
    if tipos_unidade:
        params["tiposUnidade"] = tipos_unidade
    if tipos_escola:
        params["tiposEscola"] = tipos_escola
    if nome_escola:
        params["nomeEscola"] = nome_escola
    if codigo_eol:
        params["codigoEol"] = codigo_eol
    resp = _client.get(f"{_BASE}/escolas/equipamentos/", params=params or None)
    resp.raise_for_status()
    return resp.json()
