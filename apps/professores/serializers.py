"""Serializers do domínio professores."""

from typing import Any, cast

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers


class TextoEstritoField(serializers.CharField):
    """Valida texto sem conversão implícita de tipo."""

    def to_internal_value(self, data: Any) -> str:
        """Valida e normaliza texto informado.

        Args:
            data: Valor recebido para validação.

        Returns:
            Texto validado pelo campo.
        """
        if not isinstance(data, str):
            self.fail("invalid")
        value = super().to_internal_value(data)
        if not isinstance(value, str):
            self.fail("invalid")
        return cast(str, value)


class ListaStringSerializer(serializers.ListSerializer):
    """Valida uma lista simples de textos."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault(
            "child",
            TextoEstritoField(allow_blank=False),
        )
        kwargs.setdefault("allow_empty", False)
        super().__init__(*args, **kwargs)


@extend_schema_serializer(component_name="turmas_ids")
class TurmasIdsSerializer(serializers.ListSerializer):
    """Representa a lista de turmas informadas."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault(
            "child",
            TextoEstritoField(allow_blank=False),
        )
        kwargs.setdefault("allow_empty", False)
        super().__init__(*args, **kwargs)


class NomeServidorSerializer(serializers.Serializer):
    """Serializa dados de identificação do servidor."""

    nome = serializers.CharField()
    cpf = serializers.CharField()


class ProfessorBuscarPorRfSerializer(serializers.Serializer):
    """Serializa dados resumidos de professor."""

    nome = serializers.CharField()
    codigoRF = serializers.CharField(source="codigo_rf")


class FuncionarioEscolaSerializer(serializers.Serializer):
    """Serializa funcionário vinculado a uma escola."""

    codigoRF = serializers.CharField(source="codigo_rf")
    nomeServidor = serializers.CharField(source="nome")
    dataInicio = serializers.CharField(source="data_inicio")
    dataFim = serializers.CharField(source="data_fim", allow_null=True)
    cargo = serializers.CharField(allow_null=True)
    cdTipoFuncaoAtividade = serializers.IntegerField(
        source="codigo_tipo_funcao_atividade"
    )
    estaAfastado = serializers.BooleanField(source="esta_afastado")
    funcaoExterno = serializers.IntegerField(source="funcao_externo")
    tipoFuncaoExterno = serializers.IntegerField(source="tipo_funcao_externo")


class ProfessorTurmaSerializer(serializers.Serializer):
    """Serializa dados de turma atribuída."""

    codigoTurma = serializers.CharField(source="codigo_turma")
    dataDisponibilizacaoAulas = serializers.CharField(
        source="data_disponibilizacao_aulas"
    )
    dataAtribuicaoAula = serializers.CharField(source="data_atribuicao_aula")
