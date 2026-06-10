"""Serializers de saída do domínio de matrículas."""

from typing import Any

from rest_framework import serializers

from apps.core.utils import get_first_value


class MatriculaSerializer(serializers.Serializer):
    """Serializa dados consolidados de matrícula."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma dados de matrícula no contrato legado.

        Args:
            instance: Dicionário ou objeto com consolidação da turma.

        Returns:
            Dicionário com os campos esperados pelo legado.
        """
        return {
            "turmaCodigo": get_first_value(
                instance,
                "turma_codigo",
                "turmaCodigo",
                "codigo_turma",
                "codigoTurma",
            ),
            "quantidade": get_first_value(instance, "quantidade"),
        }
