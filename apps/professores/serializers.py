"""Serializers de saída para o domínio professores."""

from rest_framework import serializers


class NomeServidorSerializer(serializers.Serializer):
    """Serializa dados de identificação do servidor."""

    nome = serializers.CharField()
    cpf = serializers.CharField()
