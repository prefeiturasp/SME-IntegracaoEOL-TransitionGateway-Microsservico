"""Serializers DRF do domínio ProgramasEdu.

Validam o shape camelCase devolvido pelo MS-ProgramasEdu (EP-02 a EP-05) e
o repassam ao consumidor do contrato legado. Como o MS já entrega o JSON
em camelCase, os campos aqui são passthrough — sem ``source=``.
"""

from rest_framework import serializers


class TurmaPapResumoSerializer(serializers.Serializer):
    """EP-02 — Turmas PAP da UE no ano letivo."""

    codigoTurma = serializers.CharField(source="codigo_turma")
    turmaNome = serializers.CharField(source="turma_nome")


class AlunoTurmaProgramaPapSerializer(serializers.Serializer):
    """EP-03 — Verificação de alunos PAP."""

    codigoAluno = serializers.IntegerField(source="codigo_aluno")
    codigoTurma = serializers.IntegerField(source="codigo_turma")
    codigoComponente = serializers.IntegerField(source="codigo_componente")
    descricao = serializers.CharField()


class AlunoTurmaPapSerializer(serializers.Serializer):
    """EP-04 / EP-05 — Alunos PAP do ano corrente / por ano letivo."""

    anoLetivo = serializers.IntegerField(source="ano_letivo")
    codigoTurma = serializers.IntegerField(source="codigo_turma")
    codigoUe = serializers.CharField(source="codigo_ue")
    codigoDre = serializers.CharField(source="codigo_dre")
    codigoAluno = serializers.IntegerField(source="codigo_aluno")
    componenteCurricularId = serializers.IntegerField(source="componente_curricular_id")
