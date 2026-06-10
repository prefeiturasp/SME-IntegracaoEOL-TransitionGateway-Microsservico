"""Serviços do domínio de alunos."""

from typing import Any

from django.conf import settings

from apps.core.http_client import ServiceClient

_BASE = "/api/v1/alunos"

_client = ServiceClient(
    base_url=settings.SIDECAR_ALUNOS_URL,
    dominio="alunos",
    api_key=settings.SIDECAR_ALUNOS_API_KEY,
    api_key_header=settings.SIDECAR_ALUNOS_API_KEY_HEADER,
)


def get_informacoes_aluno(codigo_aluno: str) -> Any:
    """Retorna informações do aluno, ou ``None`` se não encontrado.

    Args:
        codigo_aluno: Código EOL do aluno.

    Returns:
        Payload retornado pelo sidecar, ou ``None`` quando não houver corpo.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/{codigo_aluno}/informacoes")
    resp.raise_for_status()
    return _client.json_or_none(resp)


def get_necessidades_especiais_aluno(codigo_aluno: str) -> Any:
    """Retorna a necessidade especial principal do aluno.

    Args:
        codigo_aluno: Código EOL do aluno.

    Returns:
        Lista de necessidades especiais retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/{codigo_aluno}/necessidades-especiais")
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_turmas_aluno(codigo_aluno: str) -> Any:
    """Retorna turmas do aluno.

    Args:
        codigo_aluno: Código do aluno.

    Returns:
        Lista de turmas retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/{codigo_aluno}/turmas/")
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_turmas_aluno_com_programa(codigo_aluno: str) -> Any:
    """Retorna turmas do aluno no ano corrente, incluindo turmas de programa.

    Chama o endpoint de turmas com os filtros desativados
    para tipo_turma e filtragem da situação.

    Args:
        codigo_aluno: Código do aluno.

    Returns:
        Lista de turmas (regulares e de programa) retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_aluno}/turmas/",
        params={"tipo_turma": "false", "filtrar_situacao": "false"},
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def listar_alunos(codigos_aluno: list[str]) -> Any:
    """Retorna lista de alunos pelos códigos informados.

    Args:
        codigos_aluno: Códigos dos alunos usados no filtro.

    Returns:
        Lista de alunos retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, Any] = {"codigos_aluno": codigos_aluno}
    resp = _client.get(f"{_BASE}/alunos", params=params)
    resp.raise_for_status()
    return _client.json_or_none(resp) or []
