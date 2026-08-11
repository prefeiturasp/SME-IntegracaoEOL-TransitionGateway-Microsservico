"""Serializers de saída para o domínio pedagógico."""

from typing import Any, cast

from rest_framework import serializers

from apps.core.datetime import (
    datetime_legado,
    formatar_datetime_legado,
    formatar_datetime_legado_us,
)

_SENTINELA_DATA = "0001-01-01T00:00:00"


def _int_ou_zero(valor: Any) -> int:
    """Retorna inteiro ou zero quando ausente.

    Args:
        valor: Valor recebido para conversão.

    Returns:
        Valor convertido para inteiro.
    """
    return int(valor) if valor is not None else 0


def _data_legado_ou_sentinela(valor: Any) -> str:
    """Retorna data formatada ou valor padrão quando ausente.

    Args:
        valor: Data recebida para formatação.

    Returns:
        Data formatada para resposta.
    """
    return datetime_legado(valor) or _SENTINELA_DATA


class CodigoTurmaField(serializers.CharField):
    """Valida codigo de turma numerico em texto."""

    def to_internal_value(self, data: Any) -> str:
        """Valida o codigo informado.

        Args:
            data: Valor recebido para validação.

        Returns:
            Codigo validado como texto.
        """
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
        """Inicializa a lista de códigos de turma.

        Args:
            *args: Argumentos posicionais do campo.
            **kwargs: Argumentos nomeados do campo.
        """
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
        """Inicializa a lista de códigos inteiros de turmas.

        Args:
            *args: Argumentos posicionais do campo.
            **kwargs: Argumentos nomeados do campo.
        """
        kwargs.setdefault("child", serializers.IntegerField())
        kwargs.setdefault("allow_empty", True)
        super().__init__(*args, **kwargs)


class CodigoComponenteListSerializer(serializers.ListSerializer):
    """Serializa uma lista de IDs de agrupamento."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Inicializa a lista de códigos de agrupamento.

        Args:
            *args: Argumentos posicionais do campo.
            **kwargs: Argumentos nomeados do campo.
        """
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

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Fixa os campos sem dados do legado com valores padrão."""
        representacao = dict(super().to_representation(instance))
        representacao["dataFim"] = None
        representacao["dataInicioTurma"] = None
        representacao["duracaoTurno"] = 0
        representacao["serieEnsino"] = None
        representacao["situacao"] = None
        representacao["tipoTurma"] = 0
        representacao["tipoTurno"] = 0
        representacao["ueCodigo"] = None
        return representacao


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


class ModalidadeEnsinoListSerializer(serializers.ListSerializer):
    """Serializa a lista de descrições de modalidades de ensino."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Inicializa a lista de descrições de modalidades de ensino.

        Args:
            *args: Argumentos posicionais do campo.
            **kwargs: Argumentos nomeados do campo.
        """
        kwargs.setdefault("child", serializers.CharField())
        kwargs.setdefault("allow_empty", True)
        super().__init__(*args, **kwargs)


class DataHoraLegadoUSField(serializers.CharField):
    """Serializa data/hora no formato ``MM/dd/yyyy HH:mm:ss``.

    Usado pelos DTOs de escolas/salas (``SalasPorUEDTO`` e afins), que não
    passam pelo conversor JSON ISO customizado dos demais controllers.
    """

    def to_representation(self, value: Any) -> Any:
        """Formata o valor de data e hora no padrão en-US."""
        return formatar_datetime_legado_us(value)


class TipoTurmaStringField(serializers.IntegerField):
    """Serializa tipo_turma como texto."""

    def to_representation(self, value: Any) -> Any:
        """Formata o tipo de turma como texto."""
        valor = super().to_representation(value)
        return str(valor) if valor is not None else None


_NOMES_TURMA_POR_SALA = {
    "codigo_turma": "codigoTurma",
    "nome_turma": "nomeTurma",
    "tipo_turma": "tipoTurma",
    "data_inicio_turma": "dataInicioTurma",
    "data_fim_turma": "dataFimTurma",
}


class TurmaPorSalaSerializer(serializers.Serializer):
    """Serializa turma por UE/tipo de sala/ano letivo."""

    codigoTurma = serializers.IntegerField(source="codigo_turma")
    nomeTurma = serializers.CharField(source="nome_turma")
    tipoTurma = TipoTurmaStringField(source="tipo_turma")
    situacao = serializers.CharField(allow_null=True)
    dataInicioTurma = DataHoraLegadoUSField(
        source="data_inicio_turma",
        allow_null=True,
    )
    dataFimTurma = DataHoraLegadoUSField(
        source="data_fim_turma",
        allow_null=True,
    )

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """Traduz os nomes canônicos (snake_case) para o contrato legado."""
        if isinstance(data, dict):
            data = {
                _NOMES_TURMA_POR_SALA.get(nome, nome): valor
                for nome, valor in data.items()
            }
        return cast(dict[str, Any], super().to_internal_value(data))


_NOMES_TURMA_POR_ESCOLA = {
    **_NOMES_TURMA_POR_SALA,
    "nome_turma_eol": "nomeTurmaEOL",
    "sigla_modalidade": "siglaModalidade",
}


class TurmaPorEscolaSerializer(serializers.Serializer):
    """Serializa turma por UE/ano letivo com sigla de modalidade."""

    codigoTurma = serializers.IntegerField(source="codigo_turma")
    nomeTurmaEOL = serializers.CharField(source="nome_turma_eol")
    nomeTurma = serializers.CharField(source="nome_turma")
    tipoTurma = TipoTurmaStringField(source="tipo_turma")
    situacao = serializers.CharField(allow_null=True)
    dataInicioTurma = DataHoraLegadoUSField(
        source="data_inicio_turma",
        allow_null=True,
    )
    dataFimTurma = DataHoraLegadoUSField(
        source="data_fim_turma",
        allow_null=True,
    )
    siglaModalidade = serializers.CharField(
        source="sigla_modalidade",
        allow_null=True,
    )

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """Traduz os nomes canônicos (snake_case) para o contrato legado."""
        if isinstance(data, dict):
            data = {
                _NOMES_TURMA_POR_ESCOLA.get(nome, nome): valor
                for nome, valor in data.items()
            }
        return cast(dict[str, Any], super().to_internal_value(data))


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


class ListagemTurmaComponenteSerializer(serializers.Serializer):
    """Serializa um item da listagem turma×componente (contrato legado)."""

    id = serializers.CharField(allow_null=True)
    turmaCodigo = serializers.CharField(
        source="turma_codigo", allow_null=True
    )  # NOSONAR
    modalidade = serializers.IntegerField(allow_null=True)  # NOSONAR
    nomeTurma = serializers.CharField(
        source="nome_turma", allow_null=True
    )  # NOSONAR
    ano = serializers.CharField(allow_null=True)  # NOSONAR
    complementoTurmaEJA = serializers.CharField(
        source="complemento_turma_eja", allow_blank=True
    )  # NOSONAR
    nomeComponenteCurricular = serializers.CharField(
        source="nome_componente_curricular", allow_null=True
    )  # NOSONAR
    componenteCurricularCodigo = serializers.IntegerField(
        source="componente_curricular_codigo", allow_null=True
    )  # NOSONAR
    turno = serializers.CharField(allow_null=True)  # NOSONAR
    territorioSaber = serializers.BooleanField(
        source="territorio_saber"
    )  # NOSONAR
    componenteCurricularTerritorioSaberCodigo = serializers.IntegerField(
        source="componente_curricular_territorio_saber_codigo"
    )  # NOSONAR
    totalRegistros = serializers.IntegerField()  # NOSONAR
    registroFuncional = serializers.CharField(allow_null=True)  # NOSONAR
    historica = serializers.BooleanField()  # NOSONAR
    tipoEscola = serializers.IntegerField()  # NOSONAR
    situacaoTurmaEscola = serializers.CharField(allow_null=True)  # NOSONAR
    dataStatusTurmaEscola = serializers.CharField(allow_null=True)  # NOSONAR
    codigoEscola = serializers.CharField(allow_null=True)  # NOSONAR
    anoLetivo = serializers.IntegerField()  # NOSONAR
    dataDisponibizacao = serializers.CharField(allow_null=True)  # NOSONAR
    etapaEnsino = serializers.IntegerField()  # NOSONAR
    tipoGradePrograma = serializers.IntegerField()  # NOSONAR
    codigoGradePrograma = serializers.IntegerField()  # NOSONAR
    descricaoGradePrograma = serializers.CharField(allow_null=True)  # NOSONAR
    serieEnsino = serializers.CharField(allow_null=True)  # NOSONAR
    nomeFiltro = serializers.CharField(allow_null=True)  # NOSONAR
    dataInicioTurma = serializers.CharField(allow_null=True)  # NOSONAR
    dataFimTurma = serializers.CharField(allow_null=True)  # NOSONAR
    cicloEnsino = serializers.IntegerField()  # NOSONAR
    tipoTurma = serializers.IntegerField()  # NOSONAR
    duracaoTurno = serializers.IntegerField()  # NOSONAR
    dataAtualizacao = serializers.CharField(allow_null=True)  # NOSONAR
    ensinoEspecial = serializers.IntegerField()  # NOSONAR
    semestre = serializers.IntegerField()  # NOSONAR
    extinta = serializers.IntegerField()  # NOSONAR
    etapaEJA = serializers.IntegerField()  # NOSONAR

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Monta o item no contrato (camelCase, tipos e defaults)."""
        d = instance if isinstance(instance, dict) else {}
        return {
            "id": d.get("id"),
            "turmaCodigo": d.get("turma_codigo"),
            "modalidade": d.get("modalidade"),
            "nomeTurma": d.get("nome_turma"),
            "ano": d.get("ano"),
            "nomeComponenteCurricular": d.get("nome_componente_curricular"),
            "componenteCurricularCodigo": d.get(
                "componente_curricular_codigo"
            ),
            "complementoTurmaEJA": d.get("complemento_turma_eja") or "",
            "componenteCurricularTerritorioSaberCodigo": (
                d.get("componente_curricular_territorio_saber_codigo") or 0
            ),
            "turno": d.get("turno"),
            "territorioSaber": bool(d.get("territorio_saber", False)),
            "totalRegistros": 0,
            "registroFuncional": d.get("registro_funcional"),
            "historica": False,
            "dataDisponibizacao": None,
            "nomeFiltro": None,
            "etapaEJA": 0,
            # Preenchidos com dado real do domínio (correção do default):
            "tipoEscola": _int_ou_zero(d.get("tipo_escola")),
            "situacaoTurmaEscola": d.get("situacao_turma_escola"),
            "dataStatusTurmaEscola": _data_legado_ou_sentinela(
                d.get("data_status_turma_escola")
            ),
            "codigoEscola": d.get("codigo_escola"),
            "anoLetivo": _int_ou_zero(d.get("ano_letivo")),
            "etapaEnsino": _int_ou_zero(d.get("etapa_ensino")),
            "tipoGradePrograma": _int_ou_zero(d.get("tipo_grade_programa")),
            "codigoGradePrograma": _int_ou_zero(
                d.get("codigo_grade_programa")
            ),
            "descricaoGradePrograma": d.get("descricao_grade_programa"),
            "serieEnsino": d.get("serie_ensino"),
            "dataInicioTurma": datetime_legado(d.get("data_inicio_turma")),
            "dataFimTurma": datetime_legado(d.get("data_fim_turma")),
            "cicloEnsino": _int_ou_zero(d.get("ciclo_ensino")),
            "tipoTurma": _int_ou_zero(d.get("tipo_turma")),
            "duracaoTurno": _int_ou_zero(d.get("duracao_turno")),
            "dataAtualizacao": _data_legado_ou_sentinela(
                d.get("data_atualizacao")
            ),
            "ensinoEspecial": int(bool(d.get("ensino_especial"))),
            "semestre": _int_ou_zero(d.get("semestre")),
            "extinta": int(bool(d.get("extinta"))),
        }


class ListagemTurmasComponentesPaginadoSerializer(serializers.Serializer):
    """Serializa a resposta paginada da listagem turma×componente."""

    items = ListagemTurmaComponenteSerializer(many=True)
    totalRegistros = serializers.IntegerField(
        source="total_registros"
    )  # NOSONAR
    totalPaginas = serializers.IntegerField(source="total_paginas")  # NOSONAR


class TurmaAtribuidaAnoSerializer(serializers.Serializer):
    """Serializa uma atribuição agrupada de Território do Saber."""

    codigo_turma = serializers.CharField(allow_null=True)
    ano_letivo = serializers.IntegerField(allow_null=True)
    nome_turma = serializers.CharField(allow_null=True)
    data_inicio_atribuicao = serializers.DateTimeField(allow_null=True)
    data_fim_atribuicao = serializers.DateTimeField(allow_null=True)
    data_fim_turma = serializers.DateTimeField(allow_null=True)
    ano_atribuicao = serializers.IntegerField(allow_null=True)
    codigo_rf = serializers.CharField(allow_null=True)
    disciplina_id = serializers.CharField(allow_null=True)
    disciplina_nome = serializers.CharField(allow_null=True)
    disciplinas_agrupadas_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_null=True,
        allow_empty=True,
        default=list,
    )
    nome_professor = serializers.CharField(allow_null=True)


class AtribuicaoTerritorioTurmaSerializer(serializers.Serializer):
    """Serializa a atribuição de Território do Saber de uma turma."""

    codigo_turma = serializers.CharField(allow_null=True, default=None)
    disciplina_id = serializers.CharField(allow_null=True, default=None)
    disciplina_nome = serializers.CharField(allow_null=True, default=None)
    disciplinas_agrupadas_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_null=True,
        allow_empty=True,
        default=list,
    )
    nome_professor = serializers.CharField(allow_null=True, default=None)
    codigo_rf = serializers.CharField(allow_null=True, default=None)
