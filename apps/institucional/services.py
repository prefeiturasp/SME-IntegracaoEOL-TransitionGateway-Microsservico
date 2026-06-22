"""Serviços do domínio institucional."""

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
    """Lista Diretorias Regionais de Educação.

    Raises:
        httpx.HTTPStatusError: Quando o serviço externo retorna status
            HTTP de erro.
    """
    resp = _client.get(f"{_BASE}/dres/")
    resp.raise_for_status()
    return resp.json()


def get_dres_por_codigos(codigos: list[str]) -> Any:
    """Filtra Diretorias Regionais de Educação por lista de códigos.

    Args:
        codigos: Lista de códigos EOL de DREs.

    Returns:
        DREs correspondentes aos códigos informados.
    """
    resp = _client.post(f"{_BASE}/dres/", payload=codigos)
    resp.raise_for_status()
    return _client.json_or_none(resp)


def get_dre(codigo_dre: str) -> Any:
    """Retorna dados de uma Diretoria Regional de Educação.

    Args:
        codigo_dre: Código da Diretoria Regional de Educação.

    Returns:
        Dados da Diretoria Regional de Educação encontrada.

    Raises:
        httpx.HTTPStatusError: Quando o serviço externo retorna status
            HTTP de erro.
    """
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/")
    resp.raise_for_status()
    return resp.json()


def get_subprefeituras_por_dre(codigo_dre: str) -> Any:
    """Lista subprefeituras vinculadas a uma Diretoria Regional de Educação.

    Args:
        codigo_dre: Código da Diretoria Regional de Educação.

    Returns:
        Subprefeituras vinculadas à DRE informada.
    """
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/subprefeituras/")
    resp.raise_for_status()
    return resp.json()


def get_escolas_por_dre(codigo_dre: str) -> Any:
    """Lista escolas vinculadas a uma Diretoria Regional de Educação.

    Args:
        codigo_dre: Código da Diretoria Regional de Educação.

    Returns:
        Escolas vinculadas à Diretoria Regional de Educação informada.

    Raises:
        httpx.HTTPStatusError: Quando o serviço externo retorna status
            HTTP de erro.
    """
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/escola/")
    resp.raise_for_status()
    return resp.json()


def get_escolas_por_dre_e_tipo(codigo_dre: str, tipo_escola: str) -> Any:
    """Lista escolas de uma Diretoria Regional de Educação por tipo.

    Args:
        codigo_dre: Código da Diretoria Regional de Educação.
        tipo_escola: Tipo de escola usado no filtro.

    Returns:
        Escolas vinculadas à Diretoria Regional de Educação e ao tipo
        informado.

    Raises:
        httpx.HTTPStatusError: Quando o serviço externo retorna status
            HTTP de erro.
    """
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/escolas/{tipo_escola}/")
    resp.raise_for_status()
    return resp.json()


def get_ues_por_dre(codigo_dre: str) -> Any:
    """Lista códigos de UEs vinculadas a uma Diretoria Regional de Educação.

    Args:
        codigo_dre: Código da Diretoria Regional de Educação.

    Returns:
        Lista de códigos de UEs da DRE informada.
    """
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/ues/")
    resp.raise_for_status()
    return resp.json()


def get_unidades_por_dre(codigo_dre: str) -> Any:
    """Lista unidades administrativas vinculadas a uma DRE.

    Args:
        codigo_dre: Código da Diretoria Regional de Educação.

    Returns:
        Unidades administrativas da DRE informada.
    """
    resp = _client.get(f"{_BASE}/dres/{codigo_dre}/unidades/")
    resp.raise_for_status()
    return resp.json()


def get_escola(codigo_escola: str) -> Any:
    """Retorna dados de uma escola.

    Args:
        codigo_escola: Código da escola.

    Returns:
        Dados da escola encontrada.

    Raises:
        httpx.HTTPStatusError: Quando o serviço externo retorna status
            HTTP de erro.
    """
    resp = _client.get(f"{_BASE}/escolas/{codigo_escola}/")
    resp.raise_for_status()
    return resp.json()


def get_dados_escola(codigo_escola: str) -> Any:
    """Retorna dados completos de uma escola.

    Args:
        codigo_escola: Código EOL da escola.

    Returns:
        Dados completos da escola encontrada.
    """
    resp = _client.get(f"{_BASE}/escolas/dados/{codigo_escola}/")
    resp.raise_for_status()
    return _client.json_or_none(resp)


def get_tipos_escolas() -> Any:
    """Lista tipos de escola cadastrados.

    Returns:
        Tipos de escola cadastrados no sidecar institucional.
    """
    resp = _client.get(f"{_BASE}/escolas/tiposEscolas/")
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
    """Lista equipamentos das unidades educacionais.

    Args:
        codigos_subprefeitura: Códigos de subprefeituras usados no filtro.
        codigos_dre: Códigos de Diretorias Regionais de Educação usados no
            filtro.
        tipos_unidade: Tipos de unidade usados no filtro.
        tipos_escola: Tipos de escola usados no filtro.
        nome_escola: Nome da escola usado no filtro.
        codigo_eol: Código EOL usado no filtro.

    Returns:
        Equipamentos das unidades educacionais encontrados.

    Raises:
        httpx.HTTPStatusError: Quando o serviço externo retorna status
            HTTP de erro.
    """
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


def get_todas_unidades() -> Any:
    """Lista todas as unidades educacionais.

    Irá retornar os dados paginados no formato {"count": int, "results": list}, percorrendo 
    as páginas usando ``limite`` e ``offset`` e consolida todos os itens em uma 
    lista única antes de responder.

    Returns:
        Todas as unidades educacionais cadastradas.

    Raises:
        httpx.HTTPStatusError: Quando o serviço externo retorna status
            HTTP de erro.
    """
    limite = 1000
    offset = 0
    acumulado: list[Any] = []

    while True:
        resp = _client.get(
            f"{_BASE}/escolas/todas-unidades/",
            params={"limite": limite, "offset": offset},
        )
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list):
            return data

        if not isinstance(data, dict):
            return []

        resultados = data.get("results")
        if not isinstance(resultados, list):
            return []

        acumulado.extend(resultados)

        total = data.get("count")
        if not isinstance(total, int):
            break

        if len(acumulado) >= total or not resultados:
            break

        offset += len(resultados)

    return acumulado


def get_tipos_unidade_educacao() -> Any:
    """Lista tipos de unidade de educação.

    Returns:
        Tipos de unidade educacional cadastrados.

    Raises:
        httpx.HTTPStatusError: Quando o serviço externo retorna status
            HTTP de erro.
    """
    resp = _client.get(f"{_BASE}/escolas/tipos_unidade_educacao/")
    resp.raise_for_status()
    return resp.json()
