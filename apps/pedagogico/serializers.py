"""Serializers de saída para o domínio pedagógico."""

from rest_framework import serializers


class ComponenteBaseSerializer(serializers.Serializer):
    """DTO mínimo com código e descrição."""

    codigo = serializers.IntegerField()
    descricao = serializers.CharField()


class ComponenteCurricularSerializer(serializers.Serializer):
    """DTO completo de componente curricular."""

    codigo = serializers.IntegerField()
    codigoComponenteTerritorioSaber = serializers.IntegerField(allow_null=True)
    codigoComponenteCurricularPai = serializers.IntegerField(allow_null=True)
    descricao = serializers.CharField()
    regencia = serializers.BooleanField()
    planejamentoRegencia = serializers.BooleanField()
    territorioSaber = serializers.BooleanField()
    turmaCodigo = serializers.CharField(allow_null=True)
    exibirComponenteEOL = serializers.BooleanField()
    professor = serializers.CharField(allow_null=True)
    codigosTerritoriosAgrupamento = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )


class ComponenteRegenciaSerializer(serializers.Serializer):
    """DTO de componente de regência com dados de turma e atribuição."""

    anoTurma = serializers.IntegerField(allow_null=True)
    anoLetivo = serializers.IntegerField()
    codigo = serializers.IntegerField()
    codigoComponenteTerritorioSaber = serializers.IntegerField(allow_null=True)
    descricao = serializers.CharField()
    territorioSaber = serializers.BooleanField()
    tipoEscola = serializers.IntegerField(allow_null=True)
    turnoTurma = serializers.IntegerField()
    componentePlanejamentoRegencia = serializers.BooleanField()
    turmaCodigo = serializers.CharField(allow_null=True)
    professor = serializers.CharField(allow_null=True)
    inicioAtribuicao = serializers.DateTimeField(allow_null=True)
    fimAtribuicao = serializers.DateTimeField(allow_null=True)


class BooleanSerializer(serializers.Serializer):
    """Wrapper de valor booleano."""

    value = serializers.BooleanField()


class ComponenteVigenciaSerializer(serializers.Serializer):
    """DTO de vigência de componente em turma."""

    componenteCurricularCodigo = serializers.CharField()
    componenteCurricularDescricao = serializers.CharField()
    turmaCodigo = serializers.CharField()
    dataInicioTurma = serializers.DateTimeField(allow_null=True)


class GradeCurricularSerializer(serializers.Serializer):
    """DTO de grade curricular por série e modalidade."""

    codigoComponenteCurricular = serializers.IntegerField()
    descricaoComponenteCurricular = serializers.CharField()
    codigoAnoTurma = serializers.CharField()
    descricaoSerieEnsino = serializers.CharField()
    codigoSerieEnsino = serializers.IntegerField()
    modalidade = serializers.IntegerField()


class ComponentesSemAtribuicaoSerializer(serializers.Serializer):
    """DTO de componente sem atribuição docente."""

    descricao = serializers.CharField()


class AgrupamentoTerritorioSerializer(serializers.Serializer):
    """DTO de agrupamento de Território do Saber."""

    codigo = serializers.IntegerField()
    codigoComponenteTerritorioSaber = serializers.IntegerField()
    codigoComponenteCurricularPai = serializers.IntegerField(allow_null=True)
    descricao = serializers.CharField()
    regencia = serializers.BooleanField()
    planejamentoRegencia = serializers.BooleanField()
    territorioSaber = serializers.BooleanField()
    turmaCodigo = serializers.CharField()
    professor = serializers.CharField(allow_null=True)
    codigosTerritoriosAgrupamento = serializers.ListField(
        child=serializers.IntegerField()
    )
