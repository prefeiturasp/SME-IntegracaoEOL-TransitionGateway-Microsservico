"""Serializers do domínio de programas educacionais."""

from datetime import datetime

from rest_framework import serializers


class DataMatriculaField(serializers.DateTimeField):
    """Serializa data_matricula em formato ISO compatível com o consumidor legado."""

    def to_representation(self, value: object) -> str | None:
        if value in (None, ""):
            return None
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if not isinstance(value, datetime):
            return super().to_representation(value)
        value = value.replace(tzinfo=None)
        texto = value.isoformat(timespec="milliseconds")
        return texto.rstrip("0").rstrip(".")


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
