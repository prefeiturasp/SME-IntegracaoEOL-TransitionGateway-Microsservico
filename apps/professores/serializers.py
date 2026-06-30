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

    codigoRF = serializers.CharField(source="codigo_rf")
    nome = serializers.CharField()


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


class FuncionarioCargoSerializer(serializers.Serializer):
    """Serializa vínculo de funcionário com cargo."""

    funcionarioRF = serializers.CharField(source="codigo_rf")
    funcionarioNome = serializers.CharField(
        allow_null=True,
    )
    cargoId = serializers.IntegerField(source="cargo_id")


class FuncionarioFuncaoAtividadeSerializer(serializers.Serializer):
    """Serializa vínculo de funcionário com função atividade."""

    funcionarioRF = serializers.CharField(source="codigo_rf")
    funcionarioNome = serializers.CharField(
        allow_null=True,
    )
    funcaoAtividadeId = serializers.IntegerField(
        source="codigo_funcao_atividade"
    )


class FuncionarioFuncaoExternaSerializer(serializers.Serializer):
    """Serializa vínculo de funcionário com função externa."""

    funcionarioCpf = serializers.CharField(source="cpf")
    funcaoExternaId = serializers.IntegerField(source="funcao_externo")


class FuncionarioFuncaoAtividadeUeSerializer(serializers.Serializer):
    """Serializa funcionário de UE por função atividade."""

    codigoRf = serializers.CharField(source="codigo_rf")
    login = serializers.SerializerMethodField(method_name="get_login")
    nomeServidor = serializers.CharField(source="nome")
    cdCargo = serializers.SerializerMethodField(method_name="get_cd_cargo")
    codigoFuncaoAtividade = serializers.IntegerField(
        source="codigo_tipo_funcao_atividade"
    )
    funcaoExterno = serializers.IntegerField(source="funcao_externo")
    tipoFuncaoExterno = serializers.IntegerField(source="tipo_funcao_externo")

    def get_login(self, _obj: Any) -> None:
        """Retorna `login` sempre nulo."""
        # A consulta legada por função não fornece login.
        return None

    def get_cd_cargo(self, obj: Any) -> int:
        """Converta o código do cargo para inteiro, usando zero como padrão."""
        valor = obj.get("codigo_cargo") if isinstance(obj, dict) else None
        if valor in (None, ""):
            return 0
        return int(str(valor))


class ProfessorTurmaSerializer(serializers.Serializer):
    """Serializa dados de turma atribuída."""

    codigoTurma = serializers.CharField(source="codigo_turma")
    dataDisponibilizacaoAulas = serializers.CharField(
        source="data_disponibilizacao_aulas"
    )
    dataAtribuicaoAula = serializers.CharField(source="data_atribuicao_aula")


class ProfessorAutoCompleteSerializer(serializers.Serializer):
    """Serializa dados resumidos de professor para autocomplete."""

    codigoRF = serializers.CharField(source="codigo_rf")
    nome = serializers.CharField(source="nome_servidor")


class TurmaAtribuidaProfessorSerializer(serializers.Serializer):
    """Serializa turma atribuída ao professor."""

    codEscola = serializers.CharField(source="cod_escola", allow_null=True)
    codTurma = serializers.IntegerField(source="cod_turma", allow_null=True)
    tipoTurma = serializers.IntegerField(source="tipo_turma", allow_null=True)
    ano = serializers.CharField(allow_null=True)
    anoLetivo = serializers.IntegerField(source="ano_letivo", allow_null=True)
    codModalidade = serializers.IntegerField(
        source="cod_modalidade", allow_null=True
    )
    codDre = serializers.CharField(source="cod_dre", allow_null=True)
    dre = serializers.CharField(allow_null=True)
    dreAbrev = serializers.CharField(source="dre_abrev", allow_null=True)
    modalidade = serializers.CharField(allow_null=True)
    nomeTurma = serializers.CharField(source="nome_turma", allow_null=True)
    semestre = serializers.IntegerField(allow_null=True)
    tipoUE = serializers.CharField(source="tipo_ue", allow_null=True)
    codTipoUE = serializers.IntegerField(source="cod_tipo_ue", allow_null=True)
    codUe = serializers.CharField(source="cod_ue", allow_null=True)
    ue = serializers.CharField(allow_null=True)
    ueAbrev = serializers.CharField(source="ue_abrev", allow_null=True)
    tipoEscola = serializers.CharField(source="tipo_escola", allow_null=True)
    codTipoEscola = serializers.IntegerField(
        source="cod_tipo_escola", allow_null=True
    )
    duracaoTurno = serializers.IntegerField(
        source="duracao_turno", allow_null=True
    )
    tipoTurno = serializers.IntegerField(source="tipo_turno", allow_null=True)
    ensinoEspecial = serializers.BooleanField(
        source="ensino_especial", allow_null=True
    )
    serieEnsino = serializers.CharField(source="serie_ensino", allow_null=True)
    dataInicioTurma = serializers.CharField(
        source="data_inicio_turma", allow_null=True
    )
    dataFimTurma = serializers.CharField(
        source="data_fim_turma", allow_null=True
    )
    extinta = serializers.BooleanField(allow_null=True)
