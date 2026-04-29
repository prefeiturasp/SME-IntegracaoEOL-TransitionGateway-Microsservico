from rest_framework import serializers


class ComponenteBaseSerializer(serializers.Serializer):
    codigo = serializers.IntegerField()
    descricao = serializers.CharField()


class ComponenteCurricularSerializer(serializers.Serializer):
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
    value = serializers.BooleanField()


class ComponenteVigenciaSerializer(serializers.Serializer):
    componenteCurricularCodigo = serializers.CharField()
    componenteCurricularDescricao = serializers.CharField()
    turmaCodigo = serializers.CharField()
    dataInicioTurma = serializers.DateTimeField(allow_null=True)


class GradeCurricularSerializer(serializers.Serializer):
    codigoComponenteCurricular = serializers.IntegerField()
    descricaoComponenteCurricular = serializers.CharField()
    codigoAnoTurma = serializers.CharField()
    descricaoSerieEnsino = serializers.CharField()
    codigoSerieEnsino = serializers.IntegerField()
    modalidade = serializers.IntegerField()


class ComponentesSemAtribuicaoSerializer(serializers.Serializer):
    descricao = serializers.CharField()


class AgrupamentoTerritorioSerializer(serializers.Serializer):
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
