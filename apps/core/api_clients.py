"""Clientes HTTP das APIs de domínio."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from django.conf import settings

from apps.core.http_client import ServiceClient

DomainName = Literal[
    "alunos",
    "institucional",
    "pedagogico",
    "professores",
    "programasedu",
]

_CLIENTS: dict[DomainName, ServiceClient] = {}


def get_api_client(domain: DomainName) -> ServiceClient:
    """Retorna o cliente HTTP cacheado para a API de um domínio."""
    client = _CLIENTS.get(domain)
    if client is None:
        client = _client_factories()[domain]()
        _CLIENTS[domain] = client
    return client


def close_api_clients() -> None:
    """Fecha todos os clientes HTTP cacheados."""
    for client in _CLIENTS.values():
        client.close()
    _CLIENTS.clear()


def _client_factories() -> dict[DomainName, Callable[[], ServiceClient]]:
    """Monta factories com as configurações atuais do Django."""
    return {
        "alunos": lambda: ServiceClient(
            base_url=settings.ALUNOS_API_URL,
            dominio="alunos",
            api_key=settings.ALUNOS_API_KEY,
            api_key_header=settings.ALUNOS_API_KEY_HEADER,
        ),
        "institucional": lambda: ServiceClient(
            base_url=settings.INSTITUCIONAL_API_URL,
            dominio="institucional",
            api_key=settings.INSTITUCIONAL_API_KEY,
            api_key_header=settings.INSTITUCIONAL_API_KEY_HEADER,
        ),
        "pedagogico": lambda: ServiceClient(
            base_url=settings.PEDAGOGICO_API_URL,
            dominio="pedagogico",
            api_key=settings.PEDAGOGICO_API_KEY,
            api_key_header=settings.PEDAGOGICO_API_KEY_HEADER,
        ),
        "professores": lambda: ServiceClient(
            base_url=settings.PROFESSORES_API_URL,
            dominio="professores",
            api_key=settings.PROFESSORES_API_KEY,
            api_key_header=settings.PROFESSORES_API_KEY_HEADER,
        ),
        "programasedu": lambda: ServiceClient(
            base_url=settings.PROGRAMASEDU_API_URL,
            dominio="programasedu",
            api_key=settings.PROGRAMASEDU_API_KEY,
            api_key_header=settings.PROGRAMASEDU_API_KEY_HEADER,
        ),
    }
