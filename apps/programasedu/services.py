"""Chamadas ao sidecar de programas educacionais."""

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


# EP-02
def listar_turmas_pap(ano_letivo: int, codigo_escola: str) -> Any:
    """EP-02. Turmas PAP da UE no ano letivo."""
    return _client.get(
        f"{_BASE}/turmas-pap/{ano_letivo}/ues/{codigo_escola}"
    ).json()


# EP-03
def verificar_alunos_pap(
    ano_letivo: int, codigos_alunos: list[str]
) -> Any:
    """EP-03. Filtra os alunos informados que estao em turmas PAP no ano."""
    params: dict[str, Any] = {"codigos_alunos": codigos_alunos}
    return _client.get(
        f"{_BASE}/alunos-pap/{ano_letivo}", params=params
    ).json()


# EP-04
def listar_alunos_pap_ano_corrente() -> Any:
    """EP-04. Todos os alunos PAP do ano corrente."""
    return _client.get(f"{_BASE}/pap/ano-corrente").json()


# EP-05
def listar_alunos_pap_por_ano(ano_letivo: int) -> Any:
    """EP-05. Todos os alunos PAP do ano letivo informado."""
    return _client.get(f"{_BASE}/pap/ano-letivo/{ano_letivo}").json()
