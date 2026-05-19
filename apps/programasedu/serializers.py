"""Serializers do domínio de programas educacionais."""

from rest_framework import serializers


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
