"""Serializers de saída para o domínio pedagógico."""

from typing import Any, cast

from rest_framework import serializers


class CodigoTurmaField(serializers.CharField):
    """Valida codigo de turma numerico em texto."""

    def to_internal_value(self, data: Any) -> str:
        """Valida o codigo informado."""
        if not isinstance(data, str):
            self.fail("invalid")
        value = cast(str, super().to_internal_value(data))
        if not value.isdecimal():
            raise serializers.ValidationError(
                "Todos os codigos devem conter apenas numeros."
            )
        return value


class CodigoTurmaListSerializer(serializers.ListSerializer):
    """Serializa lista de codigos de turma."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("child", CodigoTurmaField(allow_blank=False))
        kwargs.setdefault("allow_empty", True)
        super().__init__(*args, **kwargs)


class TurmaDadosSerializer(serializers.Serializer):
    """Serializa dados de turma no contrato legado."""

    ano = serializers.CharField(allow_null=True)
    anoLetivo = serializers.IntegerField(allow_null=True)
    codigo = serializers.IntegerField()
    tipoTurma = serializers.IntegerField(allow_null=True)
    modalidade = serializers.CharField(allow_null=True)
    codigoModalidade = serializers.IntegerField(allow_null=True)
    nomeTurma = serializers.CharField(allow_null=True)
    semestre = serializers.IntegerField(allow_null=True)
    duracaoTurno = serializers.IntegerField(allow_null=True)
    tipoTurno = serializers.IntegerField(allow_null=True)
    dataFim = serializers.CharField(allow_null=True)
    ehistorico = serializers.BooleanField()
    ensinoEspecial = serializers.BooleanField(allow_null=True)
    etapaEJA = serializers.IntegerField()
    serieEnsino = serializers.CharField(allow_null=True)
    dataInicioTurma = serializers.CharField(allow_null=True)
    extinta = serializers.BooleanField(allow_null=True)
    situacao = serializers.CharField(allow_null=True)
    ueCodigo = serializers.CharField(allow_null=True)


class ComponenteBaseSerializer(serializers.Serializer):
    """Serializa o resumo de componente curricular."""

    codigo = serializers.IntegerField()
    descricao = serializers.CharField()


class ComponenteCurricularSerializer(serializers.Serializer):
    """Serializa dados completos de componente curricular."""

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


class ComponenteRegenciaSerializer(serializers.Serializer):
    """Serializa dados de componente curricular de regência."""

    anoTurma = serializers.CharField(
        source="ano_turma", allow_null=True
    )  # NOSONAR
    anoLetivo = serializers.IntegerField(source="ano_letivo")  # NOSONAR
    codigo = serializers.IntegerField()
    codigoComponenteTerritorioSaber = serializers.IntegerField(
        source="codigo_componente_territorio_saber", allow_null=True
    )  # NOSONAR
    descricao = serializers.CharField()
    territorioSaber = serializers.BooleanField(
        source="territorio_saber"
    )  # NOSONAR
    tipoEscola = serializers.CharField(
        source="tipo_escola", allow_null=True
    )  # NOSONAR
    turnoTurma = serializers.IntegerField(
        source="turno_turma", allow_null=True
    )  # NOSONAR
    componentePlanejamentoRegencia = serializers.BooleanField(
        source="componente_planejamento_regencia"
    )  # NOSONAR
    turmaCodigo = serializers.CharField(
        source="turma_codigo", allow_null=True
    )  # NOSONAR
    professor = serializers.CharField(allow_null=True)
    inicioAtribuicao = serializers.DateTimeField(
        source="inicio_atribuicao", allow_null=True
    )  # NOSONAR
    fimAtribuicao = serializers.DateTimeField(
        source="fim_atribuicao", allow_null=True
    )  # NOSONAR


class GradeCurricularSerializer(serializers.Serializer):
    """Serializa dados da grade curricular por ano letivo."""

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
