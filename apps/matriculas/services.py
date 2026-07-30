"""Serviços do domínio de matrículas."""

from typing import Any

from django.conf import settings

from apps.core.http_client import ServiceClient

_BASE = "/api/v1/alunos/matriculas"
_BASE_ALUNOS = "/api/v1/alunos"

_client = ServiceClient(
    base_url=settings.ALUNOS_API_URL,
    dominio="matriculas",
    api_key=settings.ALUNOS_API_KEY,
    api_key_header=settings.ALUNOS_API_KEY_HEADER,
)


def get_matriculas_ano_atual(ano_letivo: int, ue_codigo: str) -> Any:
    """Retorna matrículas consolidadas do ano letivo informado.

    Args:
        ano_letivo: Ano letivo usado no filtro.
        ue_codigo: Código da unidade educacional.

    Returns:
        Lista de matrículas consolidadas por turma.

    Raises:
        httpx.HTTPStatusError: Se a API retornar status de erro.
        httpx.RequestError: Se a API estiver inacessível.
    """
    resp = _client.get(
        _BASE,
        params={"ano_letivo": ano_letivo, "ue_codigo": ue_codigo},
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_matriculas_anos_anteriores(ano_letivo: int, ue_codigo: str) -> Any:
    """Retorna matrículas históricas consolidadas por turma.

    Args:
        ano_letivo: Ano letivo usado no filtro.
        ue_codigo: Código da unidade educacional.

    Returns:
        Lista de matrículas históricas consolidadas por turma.

    Raises:
        httpx.HTTPStatusError: Se a API retornar status de erro.
        httpx.RequestError: Se a API estiver inacessível.
    """
    resp = _client.get(
        f"{_BASE}/anos-anteriores",
        params={"ano_letivo": ano_letivo, "ue_codigo": ue_codigo},
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_total_matriculas_por_turno_ue(ue_codigo: str) -> Any:
    """Retorna o total de matrículas por turno da UE.

    Args:
        ue_codigo: Código da unidade educacional.

    Returns:
        Objeto agregado no contrato legado com total de matrículas e
        distribuição por turnos.

    Raises:
        httpx.HTTPStatusError: Se a API retornar status de erro.
        httpx.RequestError: Se a API estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/escolas/{ue_codigo}/quantidades")
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_total_matriculas_por_turno_dre(dre_codigo: str) -> Any:
    """Retorna o total de matrículas por turno da DRE.

    Args:
        dre_codigo: Código da DRE.

    Returns:
        Lista agregada por escola no contrato legado, com total de
        matrículas e distribuição por turnos.

    Raises:
        httpx.HTTPStatusError: Se a API retornar status de erro.
        httpx.RequestError: Se a API estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/escolas/dre/{dre_codigo}/quantidades")
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_quantidade_alunos_por_turma_escola(codigo_escola: str) -> Any:
    """Retorna quantidade de alunos por turma na escola.

    Args:
        codigo_escola: Código da unidade escolar.

    Returns:
        Lista agregada por turma.

    Raises:
        httpx.HTTPStatusError: Se a API retornar status de erro.
        httpx.RequestError: Se a API estiver inacessível.
    """
    resp = _client.get(
        f"{_BASE_ALUNOS}/escolas/{codigo_escola}/alunos/quantidade"
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_matriculas_aluno_escola(
    codigo_escola: str,
    codigo_aluno: str,
) -> Any:
    """Retorna matrículas de um aluno na escola.

    Args:
        codigo_escola: Código da unidade escolar.
        codigo_aluno: Código EOL do aluno.

    Returns:
        Lista de matrículas do aluno na escola.

    Raises:
        httpx.HTTPStatusError: Se a API retornar status de erro.
        httpx.RequestError: Se a API estiver inacessível.
    """
    resp = _client.get(
        f"{_BASE_ALUNOS}/escolas/{codigo_escola}/aluno/{codigo_aluno}/matriculas"
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []
