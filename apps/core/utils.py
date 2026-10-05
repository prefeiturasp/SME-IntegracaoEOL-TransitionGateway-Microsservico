"""Utilitários compartilhados entre apps."""

from collections.abc import Mapping
from typing import Any

# Elegibilidade das turmas históricas do professor (contrato legado).
ETAPAS_TURMAS_HISTORICAS = frozenset(
    {1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 17}
)
TIPOS_ESCOLA_TURMAS_HISTORICAS = frozenset({1, 2, 3, 4, 16, 28, 31})


def turma_historica_elegivel(turma: Mapping[str, Any]) -> bool:
    """Verifica se a turma atende às etapas e escolas do contrato legado.

    A etapa de ensino é obrigatória; o tipo de escola só restringe quando
    presente no payload.

    Args:
        turma: Dados da turma retornados pelo serviço pedagógico.

    Returns:
        ``True`` quando a turma é elegível para o contrato legado.
    """
    if turma.get("codigo_etapa_ensino") not in ETAPAS_TURMAS_HISTORICAS:
        return False
    tipo_escola = turma.get("tipo_escola")
    if tipo_escola is None:
        return True
    return tipo_escola in TIPOS_ESCOLA_TURMAS_HISTORICAS


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
