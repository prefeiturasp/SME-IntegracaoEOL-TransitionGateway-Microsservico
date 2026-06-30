"""Fields de serialização compartilhados entre apps."""

from typing import Any

from rest_framework import serializers

from apps.core.datetime import datetime_legado


class DataHoraLegadoComZField(serializers.Field):
    """Serializa data/hora com o sufixo publicado."""

    def __init__(self, **kwargs: Any) -> None:
        """Configura o campo para aceitar valores nulos.

        Args:
            **kwargs: Opções repassadas ao campo do DRF.
        """
        kwargs.setdefault("allow_null", True)
        super().__init__(**kwargs)

    def to_representation(self, value: Any) -> str | None:
        """Serializa a data/hora no formato publicado.

        Args:
            value: Data ou data/hora recebida para serialização.

        Returns:
            Data/hora formatada ou `None` quando não houver valor.
        """
        texto = datetime_legado(value)
        return None if texto is None else f"{texto}Z"


class InteiroBooleanoField(serializers.Field):
    """Serializa valor booleano como zero ou um."""

    def to_representation(self, value: Any) -> int:
        """Serializa o valor como indicador numérico.

        Args:
            value: Valor recebido para serialização.

        Returns:
            Um para valor verdadeiro ou zero para valor falso.
        """
        return int(bool(value))


class ConstanteLegadoField(serializers.Field):
    """Serializa um valor constante do contrato legado."""

    def __init__(self, valor: Any, **kwargs: Any) -> None:
        """Fixa o valor constante a ser serializado.

        Args:
            valor: Valor constante retornado na serialização.
            **kwargs: Opções repassadas ao campo do DRF.
        """
        self._valor = valor
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, _value: Any) -> Any:
        """Retorna o valor constante configurado.

        Args:
            _value: Valor de entrada, ignorado.

        Returns:
            O valor constante fixado na construção.
        """
        return self._valor
