"""Serviços do domínio de professores."""

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
    """Retorna o nome do professor.

    Args:
        rf_professor: Registro funcional do professor.

    Returns:
        Nome do professor, texto retornado pelo serviço ou `None`.
    """
    resp = _client.get(f"{_BASE}/{rf_professor}")
    data = _client.json_or_none(resp)
    if isinstance(data, dict):
        return data.get("nome")
    return data


def get_validade_professor(codigo_rf: str) -> Any:
    """Verifica a validade do professor.

    Args:
        codigo_rf: Código RF do professor.

    Returns:
        Indicador de validade do professor.
    """
    resp = _client.get(f"{_BASE}/{codigo_rf}/validade")
    return resp.json()


def get_funcionario_ativo(registro_funcional: str) -> Any:
    """Verifica se o funcionário está ativo.

    Args:
        registro_funcional: Registro funcional do funcionário.

    Returns:
        Indicador de atividade do funcionário.
    """
    resp = _client.get(
        f"{_BASE_ACESSOS}/funcionario-ativo/{registro_funcional}"
    )
    return resp.json()


def get_nome_servidor(registro_funcional: str) -> Any:
    """Retorna dados de identificação do servidor.

    Args:
        registro_funcional: Registro funcional do servidor.

    Returns:
        Dados de identificação do servidor ou `None`.
    """
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS}/nome-servidor/{registro_funcional}"
    )
    return _client.json_or_none(resp)
