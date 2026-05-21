"""Serviços do domínio de programas educacionais."""

from typing import Any

from django.conf import settings

from apps.core.http_client import ServiceClient

_BASE = "/api/v1/programasedu/alunos"

_client = ServiceClient(
    base_url=settings.SIDECAR_PROGRAMASEDU_URL,
    dominio="programasedu",
    api_key=settings.SIDECAR_PROGRAMASEDU_API_KEY,
    api_key_header=settings.SIDECAR_PROGRAMASEDU_API_KEY_HEADER,
)


def listar_turmas_pap(ano_letivo: int, codigo_escola: str) -> Any:
    """Lista turmas PAP da UE no ano letivo.

    Args:
        ano_letivo: Ano letivo usado na consulta.
        codigo_escola: Código da unidade educacional.

    Returns:
        Turmas PAP encontradas para a unidade educacional.
    """
    return _client.get(
        f"{_BASE}/turmas-pap/{ano_letivo}/ues/{codigo_escola}"
    ).json()


def verificar_alunos_pap(ano_letivo: int, codigos_alunos: list[str]) -> Any:
    """Verifica alunos vinculados a turmas PAP no ano letivo.

    Args:
        ano_letivo: Ano letivo usado na consulta.
        codigos_alunos: Códigos dos alunos verificados.

    Returns:
        Alunos encontrados em turmas PAP.
    """
    params: dict[str, Any] = {"codigos_alunos": codigos_alunos}
    return _client.get(
        f"{_BASE}/alunos-pap/{ano_letivo}", params=params
    ).json()


def listar_alunos_pap_ano_corrente() -> Any:
    """Lista alunos PAP do ano corrente.

    Returns:
        Alunos PAP vinculados a turmas no ano corrente.
    """
    return _client.get(f"{_BASE}/pap/ano-corrente").json()


def listar_alunos_pap_por_ano(ano_letivo: int) -> Any:
    """Lista alunos PAP do ano letivo informado.

    Args:
        ano_letivo: Ano letivo usado na consulta.

    Returns:
        Alunos PAP do ano letivo informado.
    """
    return _client.get(f"{_BASE}/pap/ano-letivo/{ano_letivo}").json()
