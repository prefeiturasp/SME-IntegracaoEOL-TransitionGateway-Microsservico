"""Serializers de saída para o domínio professores."""

from rest_framework import serializers


class NomeServidorSerializer(serializers.Serializer):
    """Serializer responsável pelo retorno do nome e CPF do servidor."""

    nome = serializers.CharField()
    cpf = serializers.CharField()
