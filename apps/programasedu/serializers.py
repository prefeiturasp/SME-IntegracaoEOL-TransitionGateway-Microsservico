"""Serializers do domínio de programas educacionais."""

from datetime import date, datetime, timedelta, timezone
from typing import Any

from rest_framework import serializers

# Fuso de São Paulo (UTC-3, sem horário de verão desde 2019).
# fuso para reproduzir o tempo decorrido.
_FUSO = timezone(timedelta(hours=-3))


class DataMatriculaField(serializers.DateTimeField):
    """Serializa data_matricula em ISO para o consumidor legado."""

    def to_representation(self, value: Any) -> str:
        """Serialize a data em ISO, removendo zeros à direita."""
        if value in (None, ""):
            return None  # type: ignore[return-value]
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if not isinstance(value, datetime):
            return super().to_representation(value)
        value = value.replace(tzinfo=None)
        texto = value.isoformat(timespec="milliseconds")
        return texto.rstrip("0").rstrip(".")


class LegadoDateTimeField(serializers.CharField):
    """Serializa datas em ISO-8601 com sentinela para valores ausentes.

    Usa separador ``T``, remove zeros à direita da fração de segundos e
    aplica o sufixo ``Z`` aos valores reais. Datas ausentes viram a
    sentinela ``0001-01-01T00:00:00`` (sem ``Z``) em vez de ``null``.
    """

    _SENTINELA = "0001-01-01T00:00:00"

    def get_attribute(self, instance: object) -> str | None:
        """Retorna o valor do atributo ou a sentinela se for None."""
        value = super().get_attribute(instance)
        return "" if value is None else value

    def to_representation(self, value: object) -> str:
        """Serializa o valor em ISO-8601 ou retorna a sentinela."""
        if value in (None, ""):
            return self._SENTINELA
        dt = self._para_datetime(value)
        if dt is None:
            return str(value).strip()
        if dt.year <= 1:
            return self._SENTINELA
        if dt.tzinfo is not None:
            dt = dt.astimezone(_FUSO)
        texto = dt.replace(tzinfo=None).isoformat(timespec="microseconds")
        if "." in texto:
            texto = texto.rstrip("0").rstrip(".")
        return f"{texto}Z"

    @staticmethod
    def _para_datetime(value: object) -> datetime | None:
        """Converta o valor para datetime, retornando None quando inválido."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(
                    value.strip().replace("Z", "+00:00")
                )
            except ValueError:
                return None
        return None


class TurmaPapResumoSerializer(serializers.Serializer):
    """Serializa o resumo de turmas PAP da UE."""

    codigoTurma = serializers.CharField(source="codigo_turma")
    turmaNome = serializers.CharField(source="turma_nome")


class AlunoTurmaProgramaPapSerializer(serializers.Serializer):
    """Serializa a verificação de alunos em turmas PAP."""

    codigoAluno = serializers.IntegerField(source="codigo_aluno")
    codigoTurma = serializers.IntegerField(source="codigo_turma")
    codigoComponente = serializers.IntegerField(source="codigo_componente")
    descricao = serializers.CharField()


class AlunoTurmaPapSerializer(serializers.Serializer):
    """Serializa alunos vinculados a turmas PAP."""

    anoLetivo = serializers.IntegerField(source="ano_letivo")
    codigoTurma = serializers.IntegerField(source="codigo_turma")
    codigoUe = serializers.CharField(source="codigo_ue")
    codigoDre = serializers.CharField(source="codigo_dre")
    codigoAluno = serializers.IntegerField(source="codigo_aluno")
    componenteCurricularId = serializers.IntegerField(
        source="componente_curricular_id"
    )


class ComponenteTurmaProgramaAlunoSerializer(serializers.Serializer):
    """Serializa componentes das turmas de programa do aluno."""

    codigoAluno = serializers.CharField(source="codigo_aluno")
    codigoTurma = serializers.IntegerField(source="codigo_turma")
    codigoComponenteCurricular = serializers.IntegerField(
        source="codigo_componente_curricular"
    )
    nomeComponenteCurricular = serializers.CharField(
        source="nome_componente_curricular"
    )


class DadosSrmPaeeColaborativoSerializer(serializers.Serializer):
    """Serializa dados de SRM/PAEE colaborativo do aluno."""

    codigoTurma = serializers.IntegerField(source="codigo_turma")
    codigoEscola = serializers.CharField(source="codigo_escola")
    turno = serializers.CharField()
    componente = serializers.CharField()
    codigoComponente = serializers.IntegerField(source="codigo_componente")
    codigoAluno = serializers.IntegerField(source="codigo_aluno")
    situacaoMatricula = serializers.CharField(source="situacao_matricula")
    dataMatricula = DataMatriculaField(source="data_matricula")


class TurmaSrmRegularDoAlunoSerializer(serializers.Serializer):
    """Serializa turmas SRM e regulares do aluno em camelCase."""

    codigoAluno = serializers.IntegerField(source="codigo_aluno")
    tipoTurno = serializers.IntegerField(source="tipo_turno", allow_null=True)
    anoLetivo = serializers.IntegerField(source="ano_letivo")
    nomeAluno = serializers.CharField(source="nome_aluno", allow_null=True)
    nomeSocialAluno = serializers.CharField(
        source="nome_social_aluno", allow_null=True
    )
    codigoSituacaoMatricula = serializers.IntegerField(
        source="codigo_situacao_matricula", allow_null=True
    )
    situacaoMatricula = serializers.CharField(
        source="situacao_matricula", allow_null=True
    )
    dataSituacao = LegadoDateTimeField(source="data_situacao")
    dataNascimento = LegadoDateTimeField(source="data_nascimento")
    numeroAlunoChamada = serializers.CharField(
        source="numero_aluno_chamada", allow_null=True
    )
    codigoTurma = serializers.IntegerField(source="codigo_turma")
    nomeResponsavel = serializers.CharField(
        source="nome_responsavel", allow_null=True
    )
    tipoResponsavel = serializers.CharField(
        source="tipo_responsavel", allow_null=True
    )
    celularResponsavel = serializers.CharField(
        source="celular_responsavel", allow_null=True
    )
    dataAtualizacaoContato = LegadoDateTimeField(
        source="data_atualizacao_contato"
    )
    codigoTipoTurma = serializers.IntegerField(
        source="codigo_tipo_turma", allow_null=True
    )
    turmaNome = serializers.CharField(source="turma_nome", allow_null=True)
    etapaEnsino = serializers.IntegerField(
        source="etapa_ensino", allow_null=True
    )
    cicloEnsino = serializers.IntegerField(
        source="ciclo_ensino", allow_null=True
    )
    descEtapaEnsino = serializers.CharField(
        source="desc_etapa_ensino", allow_null=True
    )
    descCicloEnsino = serializers.CharField(
        source="desc_ciclo_ensino", allow_null=True
    )
    dataAtualizacaoTabela = LegadoDateTimeField(
        source="data_atualizacao_tabela"
    )
