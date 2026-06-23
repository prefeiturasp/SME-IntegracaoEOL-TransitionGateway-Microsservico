"""Serializers de saída para o domínio pedagógico."""

from typing import Any, cast

from rest_framework import serializers

from apps.core.datetime import formatar_datetime_legado


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


class AnosLetivosVigentesQuerySerializer(serializers.Serializer):
    """Valida o filtro de anos letivos vigentes."""

    anos_letivos_vigente = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )


class CodigoTurmaInteiroListSerializer(serializers.ListSerializer):
    """Serializa uma lista de códigos inteiros de turmas."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("child", serializers.IntegerField())
        kwargs.setdefault("allow_empty", True)
        super().__init__(*args, **kwargs)


class CodigoComponenteListSerializer(serializers.ListSerializer):
    """Serializa uma lista de IDs de agrupamento."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("child", serializers.IntegerField())
        kwargs.setdefault("allow_empty", True)
        super().__init__(*args, **kwargs)


class ItinerarioEnsinoMedioSerializer(serializers.Serializer):
    """Serializa um itinerário do ensino médio."""

    id = serializers.IntegerField()
    nome = serializers.CharField()
    serie = serializers.IntegerField()

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """Valida os tipos recebidos do contrato legado."""
        if isinstance(data, dict):
            identificador = data.get("id")
            if not isinstance(identificador, int) or isinstance(
                identificador,
                bool,
            ):
                raise serializers.ValidationError(
                    {"id": "Deve ser um número inteiro."}
                )

            if not isinstance(data.get("nome"), str):
                raise serializers.ValidationError(
                    {"nome": "Deve ser um texto válido."}
                )

            serie = data.get("serie")
            if not isinstance(serie, str) or not serie.isdecimal():
                raise serializers.ValidationError(
                    {"serie": "Deve ser um texto numérico."}
                )

        return cast(dict[str, Any], super().to_internal_value(data))


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


class TurmaHistoricaGeralSerializer(serializers.Serializer):
    """Serializa uma turma histórica geral."""

    ano = serializers.CharField()
    anoLetivo = serializers.IntegerField(source="ano_letivo")
    codigo = serializers.IntegerField()
    tipoTurma = serializers.IntegerField(
        source="tipo_turma",
        allow_null=True,
        default=0,
    )
    modalidade = serializers.CharField()
    codigoModalidade = serializers.IntegerField(
        source="codigo_modalidade",
    )
    nomeTurma = serializers.CharField(source="nome_turma")
    semestre = serializers.IntegerField()
    duracaoTurno = serializers.IntegerField(
        source="duracao_turno",
        allow_null=True,
        default=0,
    )
    tipoTurno = serializers.IntegerField(
        source="tipo_turno",
        allow_null=True,
        default=0,
    )
    dataFim = serializers.CharField(
        source="data_fim",
        allow_null=True,
        default=None,
    )
    ehistorico = serializers.BooleanField(
        allow_null=True,
        default=False,
    )
    ensinoEspecial = serializers.BooleanField(
        source="ensino_especial",
        allow_null=True,
        default=False,
    )
    etapaEJA = serializers.IntegerField(
        source="etapa_eja",
        allow_null=True,
        default=0,
    )
    serieEnsino = serializers.CharField(
        source="serie_ensino",
        allow_null=True,
        default=None,
    )
    dataInicioTurma = serializers.CharField(
        source="data_inicio_turma",
        allow_null=True,
        default=None,
    )
    extinta = serializers.BooleanField(
        allow_null=True,
        default=False,
    )
    situacao = serializers.CharField(
        allow_null=True,
        default=None,
    )
    ueCodigo = serializers.CharField(
        source="ue_codigo",
        allow_null=True,
        default=None,
    )

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """Traduz os nomes canônicos para o contrato legado."""
        if isinstance(data, dict):
            nomes_legado = {
                "ano_letivo": "anoLetivo",
                "tipo_turma": "tipoTurma",
                "codigo_modalidade": "codigoModalidade",
                "nome_turma": "nomeTurma",
                "duracao_turno": "duracaoTurno",
                "tipo_turno": "tipoTurno",
                "data_fim": "dataFim",
                "ensino_especial": "ensinoEspecial",
                "etapa_eja": "etapaEJA",
                "serie_ensino": "serieEnsino",
                "data_inicio_turma": "dataInicioTurma",
                "ue_codigo": "ueCodigo",
            }
            data = {
                nomes_legado.get(nome, nome): valor
                for nome, valor in data.items()
            }
        return cast(dict[str, Any], super().to_internal_value(data))


class DataHoraLegadoField(serializers.CharField):
    """Serializa data e hora no formato esperado pelo legado."""

    def to_representation(self, value: Any) -> Any:
        """Formata o valor de data e hora."""
        return formatar_datetime_legado(value)


class ComponenteSincronizacaoInstitucionalSerializer(serializers.Serializer):
    """Serializa o componente associado à turma."""

    nomeComponenteCurricular = serializers.CharField(
        source="nome_componente_curricular"
    )
    componenteCurricularCodigo = serializers.IntegerField(
        source="componente_curricular_codigo"
    )
    registroFuncional = serializers.CharField(
        source="registro_funcional",
        allow_null=True,
    )
    dataDisponibizacao = DataHoraLegadoField(
        source="data_disponibizacao",
        allow_null=True,
    )


class SincronizacaoInstitucionalTurmaSerializer(serializers.Serializer):
    """Serializa os dados institucionais de uma turma."""

    ano = serializers.CharField(allow_null=True)
    anoLetivo = serializers.IntegerField(
        source="ano_letivo",
        allow_null=True,
    )
    codigo = serializers.IntegerField()
    tipoTurma = serializers.IntegerField(
        source="tipo_turma",
        allow_null=True,
    )
    modalidade = serializers.SerializerMethodField()
    codigoModalidade = serializers.IntegerField(
        source="codigo_modalidade",
        allow_null=True,
    )
    nomeTurma = serializers.CharField(
        source="nome_turma",
        allow_null=True,
    )
    semestre = serializers.IntegerField(allow_null=True)
    duracaoTurno = serializers.IntegerField(
        source="duracao_turno",
        allow_null=True,
    )
    tipoTurno = serializers.IntegerField(
        source="tipo_turno",
        allow_null=True,
    )
    dataFimTurma = DataHoraLegadoField(
        source="data_fim_turma",
        allow_null=True,
    )
    ensinoEspecial = serializers.BooleanField(
        source="ensino_especial",
        allow_null=True,
    )
    etapaEJA = serializers.IntegerField(
        source="etapa_eja",
        allow_null=True,
    )
    serieEnsino = serializers.CharField(
        source="serie_ensino",
        allow_null=True,
    )
    dataInicioTurma = DataHoraLegadoField(
        source="data_inicio_turma",
        allow_null=True,
    )
    extinta = serializers.BooleanField(allow_null=True)
    situacao = serializers.CharField(allow_null=True)
    ueCodigo = serializers.CharField(
        source="ue_codigo",
        allow_null=True,
    )
    dataAtualizacao = DataHoraLegadoField(
        source="data_atualizacao",
        allow_null=True,
    )
    dataStatusTurmaEscola = DataHoraLegadoField(
        source="data_status_turma_escola",
        allow_null=True,
    )
    etapaEnsino = serializers.IntegerField(
        source="etapa_ensino",
        allow_null=True,
    )
    cicloEnsino = serializers.IntegerField(
        source="ciclo_ensino",
        allow_null=True,
    )
    tipoEscola = serializers.IntegerField(
        source="tipo_escola",
        allow_null=True,
    )
    descricaoGradePrograma = serializers.CharField(
        source="descricao_grade_programa",
        allow_null=True,
    )
    tipoGradePrograma = serializers.IntegerField(
        source="tipo_grade_programa",
        allow_null=True,
    )
    codigoGradePrograma = serializers.IntegerField(
        source="codigo_grade_programa",
        allow_null=True,
    )
    nomeFiltro = serializers.CharField(
        source="nome_filtro",
        allow_null=True,
    )
    componentes = ComponenteSincronizacaoInstitucionalSerializer(many=True)

    def get_modalidade(self, obj: Any) -> str | None:
        """Retorna o código da modalidade como texto."""
        if isinstance(obj, dict):
            codigo_modalidade = obj.get("codigo_modalidade")
        else:
            codigo_modalidade = getattr(obj, "codigo_modalidade", None)
        if codigo_modalidade is None:
            return None
        return str(codigo_modalidade)


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


class DadosAulaTurmaSerializer(serializers.Serializer):
    """Serializa dados de aula por turma no contrato legado."""

    componenteCurricularCodigo = serializers.CharField()
    componenteCurricularDescricao = serializers.CharField()
    turmaCodigo = serializers.CharField()
    dataInicioTurma = serializers.CharField(allow_null=True)


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
