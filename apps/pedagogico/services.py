"""Chamadas ao sidecar pedagógico."""

from typing import Any

from django.conf import settings

from apps.core.http_client import ServiceClient

_BASE = "/api/v1/pedagogico/componentes-curriculares"

_client = ServiceClient(
    base_url=settings.SIDECAR_PEDAGOGICO_URL,
    dominio="pedagogico",
    api_key=settings.SIDECAR_PEDAGOGICO_API_KEY,
    api_key_header=settings.SIDECAR_PEDAGOGICO_API_KEY_HEADER,
)


def get_componentes_curriculares() -> Any:
    """Retorna o catálogo completo de componentes curriculares."""
    return _client.get(_BASE).json()


def get_componentes_por_turmas_ue(
    ue_id: str,
    turmas: list[str],
) -> Any:
    """Retorna componentes curriculares das turmas de uma UE."""
    params: dict[str, Any] = {"turmas": turmas}

    return _client.get(
        f"{_BASE}/ues/{ue_id}/turmas",
        params=params,
    ).json()


def get_componentes_turmas_programa(
    ue_id: str,
    modalidade: int,
    ano_letivo: int,
) -> Any:
    """Retorna componentes de turmas programa por UE e modalidade."""
    return _client.get(
        f"{_BASE}/ues/{ue_id}/modalidades/"
        f"{modalidade}/anos/{ano_letivo}/turmas-programa"
    ).json()


def get_componentes_ue_anos(
    ue_id: str,
    modalidade: int,
    ano_letivo: int,
    anos_escolares: list[str],
) -> Any:
    """Retorna componentes filtrados por anos escolares."""
    params: dict[str, Any] = {"anos_escolares": anos_escolares}
    path = (
        f"{_BASE}/ues/"
        f"{ue_id}/modalidades/"
        f"{modalidade}/anos/"
        f"{ano_letivo}"
    )
    return _client.get(
        path,
        params=params,
    ).json()


def get_grade_curricular(ano_letivo: int) -> Any:
    """Retorna a grade curricular completa do ano letivo."""
    return _client.get(f"{_BASE}/grade-curricular/{ano_letivo}").json()
