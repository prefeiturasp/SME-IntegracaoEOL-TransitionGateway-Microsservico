"""Utilitários compartilhados entre apps."""

from collections.abc import Mapping
from typing import Any


def get_first_value(instance: Any, *keys: str, default: Any = None) -> Any:
    """Lê o primeiro valor disponível na instância.

    Args:
        instance: Origem dos dados.
        *keys: Chaves ou atributos consultados em ordem de prioridade.
        default: Valor retornado quando nenhum campo existir.

    Returns:
        Valor encontrado ou ``default``.
    """
    if isinstance(instance, Mapping):
        for key in keys:
            if key in instance:
                return instance[key]
        return default

    for key in keys:
        if hasattr(instance, key):
            return getattr(instance, key)
    return default


def string_or_none(value: Any) -> str | None:
    """Transforma valor em string quando houver conteúdo."""
    if value in (None, ""):
        return None
    return str(value)
