"""Serializers de saída do domínio de abrangência."""

from rest_framework import serializers

from apps.pedagogico.serializers import TurmaDadosSerializer


class UeEstruturaVigenteSerializer(serializers.Serializer):
    """Serializa UE no contrato de abrangência (``UeDTO``)."""

    codigo = serializers.CharField(allow_null=True)
    nome = serializers.CharField(allow_null=True)
    codTipoEscola = serializers.IntegerField(allow_null=True)
    turmas = TurmaDadosSerializer(many=True)


class DreEstruturaVigenteSerializer(serializers.Serializer):
    """Serializa DRE no contrato de abrangência (``DreDTO``)."""

    abreviacao = serializers.CharField(allow_null=True)
    codigo = serializers.CharField(allow_null=True)
    nome = serializers.CharField(allow_null=True)
    ues = UeEstruturaVigenteSerializer(many=True)


class EstruturaVigenteSerializer(serializers.Serializer):
    """Serializa a estrutura institucional vigente (DRE→UE→turma)."""

    dres = DreEstruturaVigenteSerializer(many=True)
