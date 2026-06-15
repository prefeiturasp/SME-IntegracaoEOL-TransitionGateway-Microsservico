"""Serviços do domínio de matrículas."""

from typing import Any

from django.conf import settings

from apps.core.http_client import ServiceClient

_BASE = "/api/v1/alunos/matriculas"

_client = ServiceClient(
    base_url=settings.SIDECAR_ALUNOS_URL,
    dominio="matriculas",
    api_key=settings.SIDECAR_ALUNOS_API_KEY,
    api_key_header=settings.SIDECAR_ALUNOS_API_KEY_HEADER,
)


def get_matriculas_ano_atual(ano_letivo: int, ue_codigo: str) -> Any:
    """Retorna matrículas consolidadas do ano letivo informado.

    Args:
        ano_letivo: Ano letivo usado no filtro.
        ue_codigo: Código da unidade educacional.

    Returns:
        Lista de matrículas consolidadas por turma.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(
        _BASE,
        params={"ano_letivo": ano_letivo, "ue_codigo": ue_codigo},
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []
