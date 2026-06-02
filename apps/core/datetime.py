"""Helpers para datas usadas em contratos legados."""

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

_TIMEZONE_LEGADO = ZoneInfo("America/Sao_Paulo")


def formatar_datetime_legado(value: Any) -> Any:
    """Formata data/hora UTC no padrao ISO esperado pelo legado."""
    if not isinstance(value, str) or not value.endswith("Z"):
        return value

    data = datetime.fromisoformat(value.replace("Z", "+00:00"))
    data_legado = data.astimezone(_TIMEZONE_LEGADO).replace(tzinfo=None)
    texto = data_legado.isoformat()
    if "." not in texto:
        return texto
    return texto.rstrip("0").removesuffix(".")
