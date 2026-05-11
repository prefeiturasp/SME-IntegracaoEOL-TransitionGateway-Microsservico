"""Serializers de saída para o domínio pedagógico."""

from rest_framework import serializers


class ComponenteBaseSerializer(serializers.Serializer):
    """DTO mínimo com código e descrição."""

    codigo = serializers.IntegerField()
    descricao = serializers.CharField()


class ComponenteCurricularSerializer(serializers.Serializer):
    """DTO completo de componente curricular."""

    codigo = serializers.IntegerField()
    codigoComponenteTerritorioSaber = serializers.IntegerField(
        allow_null=True
    )  # NOSONAR
    codigoComponenteCurricularPai = serializers.IntegerField(
        allow_null=True
    )  # NOSONAR
    descricao = serializers.CharField()
    regencia = serializers.BooleanField()
    planejamentoRegencia = serializers.BooleanField()  # NOSONAR
    territorioSaber = serializers.BooleanField()  # NOSONAR
    turmaCodigo = serializers.CharField(allow_null=True)  # NOSONAR
    exibirComponenteEOL = serializers.BooleanField()  # NOSONAR
    professor = serializers.CharField(allow_null=True)
    codigosTerritoriosAgrupamento = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )  # NOSONAR


class GradeCurricularSerializer(serializers.Serializer):
    """DTO de grade curricular por ano letivo."""

    codigoComponenteCurricular = serializers.IntegerField()  # NOSONAR
    descricaoComponenteCurricular = serializers.CharField()  # NOSONAR
    codigoAnoTurma = serializers.CharField()  # NOSONAR
    descricaoSerieEnsino = serializers.CharField()  # NOSONAR
    codigoSerieEnsino = serializers.IntegerField()  # NOSONAR
    modalidade = serializers.IntegerField()
