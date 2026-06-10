"""Helpers para datas usadas em contratos legados."""

from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

_TIMEZONE_LEGADO = ZoneInfo("America/Sao_Paulo")


def parse_date(value: Any) -> date | None:
    """Transforma valor bruto em data."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        raw = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(raw).date()
        except ValueError:
            try:
                return date.fromisoformat(value[:10])
            except ValueError:
                return None
    return None


def normalizar_datetime_legado(value: str) -> str:
    """Normaliza data/hora ISO para o padrão legado."""
    valor_parse = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(valor_parse)
    except ValueError:
        parsed = None

    if parsed is not None:
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(_TIMEZONE_LEGADO).replace(tzinfo=None)
        valor = parsed.isoformat()
    else:
        valor = value.replace("Z", "")

    for sep in ("+", "-"):
        pos = valor.find(sep, 10)
        if pos > -1:
            valor = valor[:pos]
            break
    if "." not in valor:
        return valor
    base, frac = valor.split(".", 1)
    frac = frac.rstrip("0")
    return base if not frac else f"{base}.{frac}"


def datetime_legado(value: Any) -> str | None:
    """Formata data/hora no padrão ISO esperado pelo legado."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return normalizar_datetime_legado(value.isoformat())
    if isinstance(value, date):
        return f"{value.isoformat()}T00:00:00"
    if isinstance(value, str):
        valor = value.strip().replace(" ", "T", 1)
        if "T" not in valor:
            return f"{valor}T00:00:00"
        return normalizar_datetime_legado(valor)
    return None


def formatar_datetime_legado(value: Any) -> Any:
    """Formata data/hora UTC no padrao ISO esperado pelo legado."""
    if not isinstance(value, str) or not value.endswith("Z"):
        return value

    return normalizar_datetime_legado(value)
