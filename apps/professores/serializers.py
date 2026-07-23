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


@extend_schema_serializer(component_name="buscar_funcionarios_por_ue")
class BuscarFuncionariosPorUeSerializer(serializers.Serializer):
    """Filtros do POST de funcionários por UE (contrato legado)."""

    codigosRfs = serializers.ListField(  # noqa: N815
        child=TextoEstritoField(allow_blank=False),
        required=False,
        allow_empty=True,
        default=list,
    )
    filtro = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


@extend_schema_serializer(component_name="buscar_turmas_elegiveis")
class BuscarTurmasElegiveisSerializer(serializers.Serializer):
    """Filtros do POST de turmas elegíveis para cópia (contrato legado)."""

    CodigoRf = serializers.CharField()
    CodigoTurma = serializers.IntegerField()
    ComponenteCurricular = serializers.IntegerField()


class DisciplinaTurmaAtribuidaSerializer(serializers.Serializer):
    """Serializa disciplina atribuída no contrato legado."""

    codDisciplina = serializers.IntegerField(source="codigo")
    codDisciplinaPai = serializers.IntegerField(
        source="codigo_componente_curricular_pai",
        allow_null=True,
        default=None,
    )
    codCompTerritorioSaber = serializers.SerializerMethodField()
    disciplina = serializers.CharField(source="descricao", allow_null=True)
    regencia = serializers.BooleanField(default=False)
    tipoEscola = serializers.SerializerMethodField()
    territorioSaber = serializers.BooleanField(
        source="territorio_saber",
        default=False,
    )
    professor = serializers.SerializerMethodField()

    def get_codCompTerritorioSaber(  # noqa: N802
        self, obj: dict[str, Any]
    ) -> int | None:
        """Retorna código de território saber."""
        return obj.get("codigo_componente_territorio_saber") or None

    def get_tipoEscola(self, obj: dict[str, Any]) -> str | None:  # noqa: N802
        """Retorna tipo de escola."""
        return obj.get("tipo_escola")

    def get_professor(self, _obj: dict[str, Any]) -> None:
        """Retorna professor da disciplina."""
        return None


class DisciplinaTurmaAgrupamentoSerializer(DisciplinaTurmaAtribuidaSerializer):
    """Serializa disciplina de turma com agrupamentos."""

    codCompTerritorioSaber = serializers.SerializerMethodField()
    tipoEscola = serializers.SerializerMethodField()
    codigosTerritoriosAgrupamento = serializers.ListField(
        source="codigos_territorios_agrupamento",
        child=serializers.IntegerField(),
        allow_empty=True,
        default=list,
    )

    def get_codCompTerritorioSaber(  # noqa: N802
        self, obj: dict[str, Any]
    ) -> int:
        """Retorna código de território saber."""
        return obj.get("codigo_componente_territorio_saber") or 0

    def get_tipoEscola(self, _obj: dict[str, Any]) -> None:  # noqa: N802
        """Retorna tipo de escola conforme contrato legado."""
        return None


class TurmaAbrangenciaLegadoSerializer(serializers.Serializer):
    """Serializa turma da abrangência no contrato legado."""

    ano = serializers.CharField(allow_null=True, default=None)
    anoLetivo = serializers.IntegerField(
        source="ano_letivo",
        allow_null=True,
        default=None,
    )
    codigo = serializers.IntegerField(allow_null=True, default=None)
    tipoTurma = serializers.SerializerMethodField()
    modalidade = serializers.CharField(allow_null=True, default=None)
    codigoModalidade = serializers.IntegerField(
        source="codigo_modalidade",
        allow_null=True,
        default=None,
    )
    nomeTurma = serializers.CharField(
        source="nome_turma",
        allow_null=True,
        default=None,
    )
    semestre = serializers.IntegerField(allow_null=True, default=None)
    duracaoTurno = serializers.IntegerField(
        source="duracao_turno",
        allow_null=True,
        default=None,
    )
    tipoTurno = serializers.IntegerField(
        source="tipo_turno",
        allow_null=True,
        default=None,
    )
    dataFim = serializers.CharField(
        source="data_fim",
        allow_null=True,
        default=None,
    )
    ehistorico = serializers.BooleanField(default=False)
    ensinoEspecial = serializers.BooleanField(
        source="ensino_especial",
        allow_null=True,
        default=None,
    )
    etapaEJA = serializers.IntegerField(
        source="etapa_eja",
        allow_null=True,
        default=None,
    )
    serieEnsino = serializers.CharField(
        source="serie_ensino",
        allow_null=True,
        default=None,
    )
    dataInicioTurma = serializers.SerializerMethodField()
    extinta = serializers.BooleanField(allow_null=True, default=None)
    situacao = serializers.CharField(allow_null=True, default=None)
    ueCodigo = serializers.CharField(
        source="ue_codigo",
        allow_null=True,
        default=None,
    )

    def get_tipoTurma(self, _obj: Any) -> int:  # noqa: N802
        """Retorna tipo de turma padrão."""
        return 0

    def get_dataInicioTurma(self, _obj: Any) -> None:  # noqa: N802
        """Retorna data de início sempre nula."""
        return None


class UeAbrangenciaLegadoSerializer(serializers.Serializer):
    """Serializa UE da abrangência no contrato legado."""

    codigo = serializers.CharField(allow_null=True, default=None)
    nome = serializers.CharField(allow_null=True, default=None)
    codTipoEscola = serializers.IntegerField(
        source="cod_tipo_escola",
        allow_null=True,
        default=None,
    )
    turmas = TurmaAbrangenciaLegadoSerializer(many=True, default=list)


class DreAbrangenciaLegadoSerializer(serializers.Serializer):
    """Serializa DRE da abrangência no contrato legado."""

    abreviacao = serializers.CharField(allow_null=True, default=None)
    codigo = serializers.CharField(allow_null=True, default=None)
    nome = serializers.CharField(allow_null=True, default=None)
    ues = UeAbrangenciaLegadoSerializer(many=True, default=list)


class GrupoAbrangenciaLegadoSerializer(serializers.Serializer):
    """Serializa grupo da abrangência no contrato legado."""

    grupoID = serializers.CharField(
        source="grupo_id",
        allow_null=True,
        default=None,
    )
    cargosId = serializers.ListField(
        source="cargos_id",
        child=serializers.IntegerField(),
        allow_empty=True,
        allow_null=True,
        default=None,
    )
    funcoesId = serializers.ListField(
        source="funcoes_id",
        child=serializers.IntegerField(),
        allow_empty=True,
        allow_null=True,
        default=None,
    )
    grupo = serializers.IntegerField(allow_null=True, default=None)
    abrangencia = serializers.IntegerField(allow_null=True, default=None)
    ehPerfilManual = serializers.BooleanField(
        source="eh_perfil_manual",
        allow_null=True,
        default=None,
    )


class AbrangenciaLegadoSerializer(serializers.Serializer):
    """Serializa abrangência do funcionário no contrato legado."""

    abrangencia = GrupoAbrangenciaLegadoSerializer(allow_null=True)
    dres = DreAbrangenciaLegadoSerializer(many=True, default=list)


class TurmasAtribuidasLegadoSerializer(serializers.Serializer):
    """Serializa turmas atribuídas no contrato legado."""

    def _valor(self, item: dict[str, Any], *campos: str) -> Any:
        """Retorna o primeiro valor encontrado."""
        for campo in campos:
            valor = item.get(campo)
            if valor is not None:
                return valor
        return None

    def to_representation(self, instance: Any) -> Any:
        """Agrupa turmas por DRE e UE."""
        if not isinstance(instance, list):
            return instance

        dres: dict[str, dict[str, Any]] = {}
        ues_por_dre: dict[tuple[str, str], dict[str, Any]] = {}
        turmas_por_ue: set[tuple[str, str, int | str | None]] = set()

        for item in instance:
            if not isinstance(item, dict):
                continue
            codigo_dre = self._valor(item, "codigo_dre", "cod_dre")
            codigo_ue = self._valor(
                item, "codigo_escola", "cod_escola", "cod_ue"
            )
            if not codigo_ue:
                continue

            chave_dre = str(codigo_dre) if codigo_dre else "__sem_dre__"
            dre = dres.setdefault(
                chave_dre,
                {
                    "abreviacao": self._valor(
                        item, "dre_abreviacao", "dre_abrev"
                    ),
                    "codigo": codigo_dre,
                    "nome": item.get("dre"),
                    "ues": [],
                },
            )
            chave_ue = (chave_dre, str(codigo_ue))
            ue = ues_por_dre.get(chave_ue)
            if ue is None:
                ue = {
                    "codigo": codigo_ue,
                    "nome": item.get("ue"),
                    "codTipoEscola": self._valor(
                        item, "codigo_tipo_escola", "cod_tipo_escola"
                    ),
                    "turmas": [],
                }
                ues_por_dre[chave_ue] = ue
                dre["ues"].append(ue)

            codigo_turma = self._valor(item, "codigo_turma", "cod_turma")
            chave_turma = (chave_dre, str(codigo_ue), codigo_turma)
            if chave_turma in turmas_por_ue:
                continue
            turmas_por_ue.add(chave_turma)

            ue["turmas"].append(
                {
                    "ano": item.get("ano"),
                    "anoLetivo": item.get("ano_letivo"),
                    "codigo": codigo_turma,
                    "tipoTurma": 0,
                    "modalidade": item.get("modalidade"),
                    "codigoModalidade": self._valor(
                        item, "codigo_modalidade", "cod_modalidade"
                    )
                    or 0,
                    "nomeTurma": item.get("nome_turma"),
                    "semestre": item.get("semestre"),
                    "duracaoTurno": item.get("duracao_turno"),
                    "tipoTurno": item.get("tipo_turno"),
                    "dataFim": None,
                    "ehistorico": False,
                    "ensinoEspecial": False,
                    "etapaEJA": 0,
                    "serieEnsino": None,
                    "dataInicioTurma": None,
                    "extinta": False,
                    "situacao": None,
                    "ueCodigo": None,
                }
            )

        for dre in dres.values():
            ues = cast(list[dict[str, Any]], dre["ues"])
            ues.sort(key=lambda ue: str(ue.get("codigo") or ""))
            for ue in ues:
                turmas = cast(list[dict[str, Any]], ue["turmas"])
                turmas.sort(
                    key=lambda turma: (
                        turma.get("codigo") is None,
                        turma.get("codigo") or 0,
                    )
                )

        dres_ordenadas = sorted(
            dres.values(), key=lambda dre: str(dre.get("codigo") or "")
        )
        return {"abrangencia": None, "dres": dres_ordenadas}


class TurmaElegivelLegadoSerializer(serializers.Serializer):
    """Serializa turma elegível no contrato legado."""

    nomeTurma = serializers.CharField(
        source="nome_turma",
        allow_null=True,
        default=None,
    )
    codTurma = serializers.IntegerField(
        source="cod_turma",
        allow_null=True,
        default=None,
    )


class FuncionarioLegadoSerializer(serializers.Serializer):
    """Serializa funcionário no contrato legado."""

    cd_Cargo = serializers.SerializerMethodField()
    codigoFuncaoAtividade = serializers.SerializerMethodField(
        method_name="get_codigo_funcao_atividade",
    )
    codigoRf = serializers.CharField(
        source="codigo_rf",
        allow_null=True,
        default=None,
    )
    funcaoExterno = serializers.IntegerField(
        source="funcao_externo",
        default=0,
    )
    login = serializers.CharField(
        source="codigo_rf",
        allow_null=True,
        default=None,
    )
    nomeServidor = serializers.CharField(
        source="nome",
        allow_null=True,
        default=None,
    )
    tipoFuncaoExterno = serializers.IntegerField(
        source="tipo_funcao_externo",
        default=0,
    )

    def get_cd_Cargo(self, _obj: Any) -> int:  # noqa: N802
        """Retorna cargo padrão."""
        return 0

    def get_codigo_funcao_atividade(self, obj: dict[str, Any]) -> int:
        """Retorna função de atividade."""
        return int(obj.get("codigo_funcao_atividade") or 0)


class FuncionarioUeLegadoSerializer(FuncionarioLegadoSerializer):
    """Serializa funcionário por UE no contrato legado."""

    def get_codigo_funcao_atividade(self, _obj: dict[str, Any]) -> int:
        """Retorna função de atividade padrão."""
        return 0


class FuncionarioSgpLegadoSerializer(serializers.Serializer):
    """Serializa funcionário SGP no contrato legado."""

    cd_Cargo = serializers.SerializerMethodField()
    codigoFuncaoAtividade = serializers.SerializerMethodField()
    codigoRf = serializers.CharField(
        source="codigo_rf",
        allow_null=True,
        default=None,
    )
    funcaoExterno = serializers.IntegerField(
        source="funcao_externo",
        default=0,
    )
    login = serializers.CharField(allow_null=True, default=None)
    nomeServidor = serializers.CharField(
        source="nome_servidor",
        allow_null=True,
        default=None,
    )
    tipoFuncaoExterno = serializers.IntegerField(
        source="tipo_funcao_externo",
        default=0,
    )

    def get_cd_Cargo(self, obj: dict[str, Any]) -> int:  # noqa: N802
        """Retorna cargo do vínculo."""
        return int(obj.get("cd_cargo") or obj.get("codigo_cargo") or 0)

    def get_codigoFuncaoAtividade(  # noqa: N802
        self, obj: dict[str, Any]
    ) -> int:
        """Retorna função de atividade."""
        return int(obj.get("codigo_funcao_atividade") or 0)


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


class SupervisorLegadoSerializer(serializers.Serializer):
    """Serializa supervisor no contrato legado."""

    codigoRF = serializers.CharField(source="codigo_rf")
    nomeServidor = serializers.CharField(source="nome_servidor")


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


class ProfessorTurmaAtribuidaSimplificadaSerializer(serializers.Serializer):
    """Serializa dados de turma atribuída ao professor simplificada."""

    codigoTurma = serializers.IntegerField(allow_null=True)
    nomeTurma = serializers.CharField(allow_null=True)
    componenteCurricular = serializers.CharField(allow_null=True)
    dataInicioAtribuicao = serializers.DateField(allow_null=True)
    dataFimAtribuicao = serializers.DateField(allow_null=True)
    ano = serializers.CharField(allow_null=True)
    etapaEnsino = serializers.IntegerField(allow_null=True)
