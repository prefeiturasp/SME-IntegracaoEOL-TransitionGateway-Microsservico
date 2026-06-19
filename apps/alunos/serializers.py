"""Serializers de saida para o contrato legado de alunos."""

from typing import Any, cast

from django.utils import timezone
from rest_framework import serializers

from apps.core.datetime import datetime_legado, parse_date
from apps.core.utils import get_first_value, string_or_none

_DATA_PADRAO_LEGADO = "0001-01-01T00:00:00"


class NumeroAlunoChamadaField(serializers.CharField):
    """Serializa número de chamada com fallback legado."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("allow_blank", True)
        kwargs.setdefault("allow_null", True)
        super().__init__(**kwargs)

    def get_attribute(self, instance: Any) -> Any:
        value = super().get_attribute(instance)
        return "0" if value in (None, "") else value

    def to_representation(self, value: Any) -> str:
        return "0" if value in (None, "") else str(value)


class DatetimeLegadoField(serializers.Field):
    """Serializa data/hora no formato ISO do contrato legado."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("allow_null", True)
        super().__init__(**kwargs)

    def to_representation(self, value: Any) -> str | None:
        return datetime_legado(value)


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


class StringOrNoneField(serializers.Field):
    """Serializa valor como string, preservando ausência como ``None``."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("allow_null", True)
        super().__init__(**kwargs)

    def to_representation(self, value: Any) -> str | None:
        return string_or_none(value)


def _idade(value: Any) -> int | None:
    """Calcula idade em anos completos.

    Args:
        value: Data de nascimento em formato aceito pelo contrato.

    Returns:
        Idade calculada, ou ``None`` quando não houver data válida.
    """
    nascimento = parse_date(value)
    if nascimento is None:
        return None
    hoje = timezone.now().date()
    idade = hoje.year - nascimento.year
    if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
        idade -= 1
    return cast(int, idade)


def _celular_responsavel(instance: Any) -> str:
    """Monta o celular do responsável.

    Args:
        instance: Dicionário ou objeto com campos de contato.

    Returns:
        Celular já informado ou concatenação de DDD e número.
    """
    celular = get_first_value(instance, "celular_responsavel")
    if celular is not None:
        return str(celular)
    ddd = get_first_value(instance, "ddd_celular")
    numero = get_first_value(instance, "numero_celular")
    if ddd or numero:
        return f"{ddd or ''}{numero or ''}"
    return ""


class EnderecoLegadoSerializer(serializers.Serializer):
    """Serializa endereço no contrato legado."""

    id = serializers.IntegerField(allow_null=True)
    nro = serializers.CharField(allow_null=True)
    complemento = serializers.CharField(allow_null=True)
    bairro = serializers.CharField(allow_null=True)
    cep = serializers.IntegerField(allow_null=True)
    nomeMunicipio = serializers.CharField(
        source="nome_municipio", allow_null=True
    )  # NOSONAR
    siglaUF = serializers.CharField(
        source="sigla_uf", allow_null=True
    )  # NOSONAR
    tipologradouro = serializers.CharField(
        source="tipo_logradouro", allow_null=True
    )  # NOSONAR
    logradouro = serializers.CharField(allow_null=True)


class AlunoInformacoesSerializer(serializers.Serializer):
    """Serializa informações cadastrais do aluno."""

    codigoAluno = serializers.IntegerField(
        source="codigo_aluno", allow_null=True
    )  # NOSONAR
    nomeAluno = serializers.CharField(
        source="nome_aluno", allow_null=True
    )  # NOSONAR
    nomeMae = serializers.CharField(
        source="nome_mae", allow_null=True
    )  # NOSONAR
    sexo = serializers.CharField(allow_null=True)
    grupoEtnico = serializers.CharField(
        source="raca_cor", allow_null=True
    )  # NOSONAR
    nacionalidade = serializers.CharField(allow_null=True)
    endereco = EnderecoLegadoSerializer(allow_null=True)
    ehImigrante = serializers.BooleanField(
        source="eh_imigrante", default=False
    )  # NOSONAR
    nis = serializers.CharField(allow_null=True)
    cns = serializers.CharField(allow_null=True)


class AlunoAutocompleteSerializer(serializers.Serializer):
    """Serializa dados de autocomplete de aluno."""

    codigoAluno = serializers.IntegerField(
        source="codigo_aluno", allow_null=True
    )  # NOSONAR
    nomeAluno = serializers.CharField(
        source="nome_aluno", allow_null=True
    )  # NOSONAR
    nomeSocialAluno = serializers.CharField(
        source="nome_social_aluno", allow_null=True
    )  # NOSONAR
    codigoTurma = serializers.IntegerField(
        source="codigo_turma", allow_null=True
    )  # NOSONAR
    numeroAlunoChamada = serializers.CharField(
        source="numero_aluno_chamada", allow_null=True
    )  # NOSONAR
    turma = serializers.CharField(allow_null=True)
    modalidade = serializers.CharField(allow_null=True)


class InformacoesAlunoTurmaSerializer(serializers.Serializer):
    """Serializa resumo de aluno em turma."""

    numeroChamada = serializers.IntegerField(
        source="numero_chamada", allow_null=True
    )  # NOSONAR
    codigoAluno = serializers.IntegerField(
        source="codigo_aluno", allow_null=True
    )  # NOSONAR
    nomeAluno = serializers.CharField(
        source="nome_aluno", allow_null=True
    )  # NOSONAR
    nomeSocialAluno = serializers.CharField(
        source="nome_social_aluno", allow_null=True
    )  # NOSONAR
    sexo = serializers.CharField(allow_null=True)
    raca = serializers.CharField(allow_null=True)
    codigoRaca = serializers.IntegerField(
        source="codigo_raca", allow_null=True
    )  # NOSONAR


class AlunoAtivoDataAulaSerializer(serializers.Serializer):
    """Serializa dados de aluno ativo e sua matrícula."""

    codigoComponenteCurricular = serializers.IntegerField(default=0)
    codigoAluno = serializers.IntegerField(
        source="codigo_aluno", allow_null=True
    )
    nomeAluno = serializers.CharField(source="nome_aluno", allow_null=True)
    dataNascimento = DataHoraLegadoComZField(source="data_nascimento")
    nomeSocialAluno = serializers.CharField(
        source="nome_social_aluno", allow_null=True
    )
    codigoSituacaoMatricula = serializers.IntegerField(
        source="codigo_situacao_matricula", allow_null=True
    )
    situacaoMatricula = serializers.CharField(
        source="situacao_matricula", allow_null=True
    )
    dataSituacao = DataHoraLegadoComZField(source="data_situacao")
    dataMatricula = DataHoraLegadoComZField(source="data_matricula")
    numeroAlunoChamada = serializers.CharField(source="numero_aluno_chamada")
    celularResponsavel = serializers.CharField(
        source="celular_responsavel",
        allow_blank=True,
        allow_null=True,
        default="",
    )
    possuiDeficiencia = InteiroBooleanoField(source="possui_deficiencia")
    transferencia_Interna = serializers.BooleanField(default=False)
    remanejado = serializers.BooleanField(default=False)
    escolaTransferencia = serializers.CharField(allow_null=True, default=None)
    turmaTransferencia = serializers.CharField(allow_null=True, default=None)
    turmaRemanejamento = serializers.CharField(allow_null=True, default=None)
    parecerConclusivo = serializers.CharField(allow_null=True, default=None)
    nomeResponsavel = serializers.CharField(
        source="nome_responsavel", allow_null=True
    )
    tipoResponsavel = serializers.IntegerField(
        source="tipo_responsavel", allow_null=True
    )
    dataAtualizacaoContato = DataHoraLegadoComZField(
        source="data_atualizacao_contato"
    )
    codigoMatricula = serializers.IntegerField(
        source="codigo_matricula", allow_null=True
    )
    sequencia = serializers.IntegerField(allow_null=True)
    tipoTurma = serializers.IntegerField(default=0)
    codigoTurma = serializers.IntegerField(
        source="codigo_turma", allow_null=True
    )
    codigoEscola = serializers.CharField(
        source="codigo_escola", allow_null=True
    )
    ano = serializers.IntegerField(source="ano_letivo", allow_null=True)
    codigoDre = serializers.CharField(source="codigo_dre", allow_null=True)
    id = serializers.IntegerField(allow_null=True, default=None)

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Serializa os campos publicados para aluno e matrícula.

        Args:
            instance: Dados do aluno e da matrícula.

        Returns:
            Campos publicados com os valores esperados pelos consumidores.
        """
        data = cast(dict[str, Any], super().to_representation(instance))
        data["codigoComponenteCurricular"] = 0
        data["transferencia_Interna"] = False
        data["remanejado"] = False
        data["escolaTransferencia"] = None
        data["turmaTransferencia"] = None
        data["turmaRemanejamento"] = None
        data["parecerConclusivo"] = None
        data["tipoTurma"] = 0
        data["id"] = None
        if data.get("celularResponsavel") is None:
            data["celularResponsavel"] = ""

        if data.get("numeroAlunoChamada") is None:
            data["numeroAlunoChamada"] = "000"
        return data


class NecessidadeEspecialSerializer(serializers.Serializer):
    """Serializa necessidade especial do aluno."""

    codigoAluno = serializers.IntegerField(
        source="codigo_aluno", allow_null=True
    )  # NOSONAR
    tipoNecessidadeEspecial = serializers.IntegerField(
        source="tipo_necessidade_especial", allow_null=True
    )  # NOSONAR
    descricaoNecessidadeEspecial = serializers.CharField(
        source="descricao_necessidade_especial", allow_null=True
    )  # NOSONAR
    tipoRecurso = serializers.IntegerField(
        source="tipo_recurso", allow_null=True
    )  # NOSONAR
    descricaoRecurso = serializers.CharField(
        source="descricao_recurso", allow_null=True
    )  # NOSONAR


class AlunoLegadoBaseSerializer(serializers.Serializer):
    """Serializa campos comuns do contrato legado de aluno e matrícula."""

    codigoAluno = serializers.IntegerField(
        source="codigo_aluno", allow_null=True
    )  # NOSONAR
    anoLetivo = serializers.IntegerField(
        source="ano_letivo", allow_null=True
    )  # NOSONAR
    nomeAluno = serializers.CharField(
        source="nome_aluno", allow_null=True
    )  # NOSONAR
    nomeSocialAluno = serializers.CharField(
        source="nome_social_aluno", allow_null=True
    )  # NOSONAR
    codigoSituacaoMatricula = serializers.IntegerField(
        source="codigo_situacao_matricula", allow_null=True
    )  # NOSONAR
    situacaoMatricula = serializers.CharField(
        source="situacao_matricula", allow_null=True
    )  # NOSONAR
    dataSituacao = DatetimeLegadoField(source="data_situacao")  # NOSONAR
    dataNascimento = DatetimeLegadoField(source="data_nascimento")  # NOSONAR
    numeroAlunoChamada = NumeroAlunoChamadaField(
        source="numero_aluno_chamada"
    )  # NOSONAR
    codigoTurma = serializers.IntegerField(
        source="codigo_turma", allow_null=True
    )  # NOSONAR
    nomeResponsavel = serializers.CharField(
        source="nome_responsavel", allow_null=True
    )  # NOSONAR
    tipoResponsavel = StringOrNoneField(source="tipo_responsavel")  # NOSONAR
    celularResponsavel = serializers.SerializerMethodField(
        method_name="get_celular_responsavel"
    )  # NOSONAR
    dataAtualizacaoContato = DatetimeLegadoField(
        source="data_atualizacao_contato"
    )  # NOSONAR
    codigoTipoTurma = serializers.IntegerField(
        source="codigo_tipo_turma", allow_null=True
    )  # NOSONAR
    dataAtualizacaoTabela = serializers.SerializerMethodField(
        method_name="get_data_atualizacao_tabela"
    )  # NOSONAR

    def get_celular_responsavel(self, instance: Any) -> str:
        """Monta o celular do responsável.

        Args:
            instance: Dicionário ou objeto com campos de contato.

        Returns:
            Celular já informado ou concatenação de DDD e número.
        """
        return _celular_responsavel(instance)

    def get_data_atualizacao_tabela(self, instance: Any) -> str | None:
        """Resolve a data de atualização com fallback do legado.

        Args:
            instance: Dicionário ou objeto com dados da matrícula.

        Returns:
            Data formatada, usando a data de situação ou o padrão legado
            como fallback.
        """
        return datetime_legado(
            get_first_value(instance, "data_atualizacao_tabela")
            or get_first_value(instance, "data_situacao")
            or _DATA_PADRAO_LEGADO
        )


class TurmaDoAlunoSerializer(AlunoLegadoBaseSerializer):
    """Serializa dados de matrícula e turma do aluno."""

    idade = serializers.SerializerMethodField()
    documentoCpf = serializers.CharField(
        source="documento_cpf", allow_null=True
    )  # NOSONAR
    dataMatricula = DatetimeLegadoField(source="data_matricula")  # NOSONAR
    codigoEscola = serializers.CharField(
        source="codigo_escola", allow_null=True
    )  # NOSONAR

    def get_idade(self, instance: Any) -> int | None:
        """Resolve a idade informada ou calculada do nascimento.

        Args:
            instance: Dicionário ou objeto com dados do aluno.

        Returns:
            Idade informada pela origem, ou calculada da data de
            nascimento quando ausente.
        """
        idade = get_first_value(instance, "idade")
        if idade is not None:
            return cast(int, idade)
        return _idade(get_first_value(instance, "data_nascimento"))


class AlunoPorCodigoSerializer(AlunoLegadoBaseSerializer):
    """Serializa dados do aluno com campos do contrato de listagem."""

    tipoTurno = serializers.IntegerField(
        source="tipo_turno", default=0
    )  # NOSONAR
    turmaNome = serializers.CharField(
        source="turma_nome", allow_null=True
    )  # NOSONAR
    etapaEnsino = serializers.CharField(
        source="etapa_ensino", allow_null=True
    )  # NOSONAR
    cicloEnsino = serializers.CharField(
        source="ciclo_ensino", allow_null=True
    )  # NOSONAR
    descEtapaEnsino = serializers.CharField(
        source="desc_etapa_ensino", allow_null=True
    )  # NOSONAR
    descCicloEnsino = serializers.CharField(
        source="desc_ciclo_ensino", allow_null=True
    )  # NOSONAR


class ResponsavelResumidoSerializer(serializers.Serializer):
    """Serializa dados resumidos de responsável."""

    id = serializers.IntegerField(allow_null=True)
    cpf = serializers.CharField(allow_null=True)
    email = serializers.CharField(allow_null=True)
    nome = serializers.CharField(allow_null=True)
    tipoResponsavel = serializers.IntegerField(
        source="tipo_responsavel", allow_null=True
    )  # NOSONAR
    dataNascimento = DatetimeLegadoField(source="data_nascimento")  # NOSONAR
    dataAtualizacao = DatetimeLegadoField(source="data_atualizacao")  # NOSONAR
    nomeMae = serializers.CharField(
        source="nome_mae", allow_null=True
    )  # NOSONAR
    dddCelular = serializers.CharField(
        source="ddd_celular", allow_null=True
    )  # NOSONAR
    numeroCelular = serializers.CharField(
        source="numero_celular", allow_null=True
    )  # NOSONAR
    codigoAluno = serializers.CharField(
        source="codigo_aluno", allow_null=True
    )  # NOSONAR
