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
        source="codigo_componente_territorio_saber", allow_null=True
    )  # NOSONAR
    codigoComponenteCurricularPai = serializers.IntegerField(
        source="codigo_componente_curricular_pai", allow_null=True
    )  # NOSONAR
    descricao = serializers.CharField()
    regencia = serializers.BooleanField()
    planejamentoRegencia = serializers.BooleanField(
        source="planejamento_regencia"
    )  # NOSONAR
    territorioSaber = serializers.BooleanField(
        source="territorio_saber"
    )  # NOSONAR
    turmaCodigo = serializers.CharField(
        source="turma_codigo", allow_null=True
    )  # NOSONAR
    exibirComponenteEOL = serializers.BooleanField(
        source="exibir_componente_eol"
    )  # NOSONAR
    professor = serializers.CharField(allow_null=True)
    codigosTerritoriosAgrupamento = serializers.ListField(
        source="codigos_territorios_agrupamento",
        child=serializers.IntegerField(),
        allow_empty=True,
    )  # NOSONAR


class GradeCurricularSerializer(serializers.Serializer):
    """DTO de grade curricular por ano letivo."""

    codigoComponenteCurricular = serializers.IntegerField(
        source="codigo_componente_curricular"
    )  # NOSONAR
    descricaoComponenteCurricular = serializers.CharField(
        source="descricao_componente_curricular"
    )  # NOSONAR
    codigoAnoTurma = serializers.CharField(
        source="codigo_ano_turma", allow_null=True
    )  # NOSONAR
    descricaoSerieEnsino = serializers.CharField(
        source="descricao_serie_ensino", allow_null=True
    )  # NOSONAR
    codigoSerieEnsino = serializers.IntegerField(
        source="codigo_serie_ensino", allow_null=True
    )  # NOSONAR
    modalidade = serializers.IntegerField()
