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


class QuantidadeAlunosPorTurmaEscolaSerializer(serializers.Serializer):
    """Serializa quantidade de alunos por turma da escola."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma dados agregados no contrato legado.

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


class MatriculaAlunoEscolaSerializer(serializers.Serializer):
    """Serializa matrícula de aluno em escola no contrato legado."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma dados de matrícula no contrato legado.

        Args:
            instance: Dicionário ou objeto com dados da matrícula.

        Returns:
            Dicionário com os campos esperados pelo legado.
        """
        return {
            "codigoAluno": get_first_value(
                instance, "codigo_aluno", "codigoAluno"
            ),
            "nomeAluno": get_first_value(
                instance, "nome_aluno", "nomeAluno"
            ),
            "nomeSocialAluno": get_first_value(
                instance, "nome_social_aluno", "nomeSocialAluno"
            ),
            "codigoSituacaoMatricula": get_first_value(
                instance,
                "codigo_situacao_matricula",
                "codigoSituacaoMatricula",
            ),
            "situacaoMatricula": get_first_value(
                instance, "situacao_matricula", "situacaoMatricula"
            ),
            "dataSituacao": get_first_value(
                instance, "data_situacao", "dataSituacao"
            ),
            "codigoTurma": get_first_value(
                instance, "codigo_turma", "codigoTurma"
            ),
            "codigoMatricula": get_first_value(
                instance, "codigo_matricula", "codigoMatricula"
            ),
            "anoLetivo": get_first_value(
                instance, "ano_letivo", "anoLetivo"
            ),
        }
