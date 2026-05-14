"""Serviços do domínio institucional — repasse ao sidecar."""

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


def get_dres() -> Any:
    resp = _client.get(f"{_BASE}/dres/")
    resp.raise_for_status()
    return resp.json()


def get_dre(codigo_dre: str) -> Any:
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/")
    resp.raise_for_status()
    return resp.json()


def get_escolas_por_dre(codigo_dre: str) -> Any:
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/escola/")
    resp.raise_for_status()
    return resp.json()


def get_escolas_por_dre_e_tipo(codigo_dre: str, tipo_escola: str) -> Any:
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/escolas/{tipo_escola}/")
    resp.raise_for_status()
    return resp.json()


def get_escola(codigo_escola: str) -> Any:
    resp = _client.get(f"{_BASE}/escolas/{codigo_escola}/")
    resp.raise_for_status()
    return resp.json()


def get_equipamentos(
    codigos_subprefeitura: list[str] | None = None,
    codigos_dre: list[str] | None = None,
    tipos_unidade: list[str] | None = None,
    tipos_escola: list[str] | None = None,
    nome_escola: str | None = None,
    codigo_eol: str | None = None,
) -> Any:
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
