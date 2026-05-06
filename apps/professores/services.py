"""Chamadas ao sidecar de professores, uma funcao por endpoint canonico."""

from typing import Any

from django.conf import settings

from apps.core.http_client import ServiceClient

_BASE = "/api/v1/professores"
_BASE_ACESSOS = f"{_BASE}/acessos"
_BASE_FUNCIONARIOS = f"{_BASE}/funcionarios"

_client = ServiceClient(
    base_url=settings.SIDECAR_PROFESSORES_URL,
    dominio="professores",
    api_key=settings.SIDECAR_PROFESSORES_API_KEY,
    api_key_header=settings.SIDECAR_PROFESSORES_API_KEY_HEADER,
)


def get_professor(rf_professor: str) -> Any:
    """Retorna somente o nome do professor."""
    resp = _client.get(f"{_BASE}/{rf_professor}")
    data = _client.json_or_none(resp)
    if isinstance(data, dict):
        return data.get("nome")
    return data


def get_validade_professor(codigo_rf: str) -> Any:
    """Verifica validade do professor pelo codigo RF."""
    resp = _client.get(f"{_BASE}/{codigo_rf}/validade")
    return resp.json()


def get_funcionario_ativo(registro_funcional: str) -> Any:
    """Verifica se o funcionario esta ativo."""
    resp = _client.get(
        f"{_BASE_ACESSOS}/funcionario-ativo/{registro_funcional}"
    )
    return resp.json()


def get_nome_servidor(registro_funcional: str) -> Any:
    """Retorna somente o nome do servidor."""
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS}/nome-servidor/{registro_funcional}"
    )
    return _client.json_or_none(resp)
