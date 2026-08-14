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


class FuncionariosPerfisQuerySerializer(serializers.Serializer):
    """Normaliza e valida filtros de funcionários por perfil."""

    mensagem_dre_ou_rf_obrigatorio = (
        "O código da Dre ou código rf/login deve ser informados."
    )

    codigo_dre = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    codigo_ue = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    codigo_rf = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    nome_servidor = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        data = kwargs.get("data")
        if data is not None:
            kwargs["data"] = {
                "codigo_dre": data.get("CodigoDre")
                or data.get("codigo_dre")
                or "",
                "codigo_ue": data.get("CodigoUe")
                or data.get("codigo_ue")
                or "",
                "codigo_rf": data.get("CodigoRf")
                or data.get("codigo_rf")
                or "",
                "nome_servidor": data.get("NomeServidor")
                or data.get("nome_servidor")
                or "",
            }
        super().__init__(*args, **kwargs)

    def validate(self, attrs: dict[str, str]) -> dict[str, str]:
        """Exige DRE ou RF e remove filtros vazios."""
        params = {chave: valor for chave, valor in attrs.items() if valor}
        if not params.get("codigo_dre") and not params.get("codigo_rf"):
            raise serializers.ValidationError(
                self.mensagem_dre_ou_rf_obrigatorio
            )
        return params


class AbrangenciaTemporariaSerializer(serializers.Serializer):
    """Normaliza parâmetros temporários de abrangência."""

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """Normaliza os parâmetros recebidos na consulta.

        Args:
            data: Parâmetros recebidos na requisição.

        Returns:
            Parâmetros temporários normalizados.
        """
        return {
            "abrangencia": self.obter_inteiro(data, "abrangencia"),
            "cargos": self.obter_inteiros(data, "cargos"),
            "funcoes": self.obter_inteiros(data, "funcoesId"),
            "grupo": self.obter_inteiro(data, "grupo"),
            "dre_codigo": self.obter_valor(data, "dreCodigo"),
            "eh_perfil_manual": (
                self.obter_valor(data, "ehPerfilManual") or ""
            ).lower()
            == "true",
        }

    def obter_valor(self, data: Any, nome: str) -> str | None:
        """Retorna um parâmetro textual simples.

        Args:
            data: Parâmetros recebidos na requisição.
            nome: Nome do parâmetro consultado.

        Returns:
            Valor informado, ou ``None`` quando ausente.
        """
        if not hasattr(data, "get"):
            return None
        return data.get(nome) or None

    def obter_inteiro(self, data: Any, nome: str) -> int | None:
        """Retorna um parâmetro inteiro simples.

        Args:
            data: Parâmetros recebidos na requisição.
            nome: Nome do parâmetro consultado.

        Returns:
            Inteiro informado, ou ``None`` quando ausente.
        """
        valor = self.obter_valor(data, nome)
        return int(valor) if valor and valor.isdigit() else None

    def obter_inteiros(self, data: Any, nome: str) -> list[int] | None:
        """Retorna parâmetros inteiros repetidos.

        Args:
            data: Parâmetros recebidos na requisição.
            nome: Nome do parâmetro consultado.

        Returns:
            Inteiros informados, ou ``None`` quando ausentes.
        """
        if not hasattr(data, "getlist"):
            return None
        valores = [
            item for item in data.getlist(nome) if item.strip().isdigit()
        ]
        return [int(item) for item in valores] or None


class DisciplinasFuncionarioPathSerializer(serializers.Serializer):
    """Valida parâmetros da consulta de disciplinas do funcionário."""

    login = serializers.CharField(allow_blank=True)
    id_perfil = serializers.CharField(allow_blank=True)
    codigo_turma = serializers.CharField(allow_blank=True)

    def validate(self, attrs: dict[str, str]) -> dict[str, str]:
        """Valida os parâmetros obrigatórios do caminho.

        Args:
            attrs: Parâmetros recebidos no caminho da rota.

        Returns:
            Parâmetros validados.

        Raises:
            ValidationError: Quando algum parâmetro obrigatório está ausente.
        """
        if not attrs["login"].strip():
            raise serializers.ValidationError("É necessário informar o login.")
        if not attrs["id_perfil"].strip():
            raise serializers.ValidationError(
                "É necessário informar o idPerfil."
            )
        if not attrs["codigo_turma"].strip():
            raise serializers.ValidationError(
                "É necessário informar o codigoTurma."
            )
        return attrs


class QueryParamsSerializer(serializers.Serializer):
    """Normaliza parâmetros simples e repetidos da consulta."""

    campos_lista: tuple[str, ...] = ()
    campos_simples: tuple[str, ...] = ()
    campos_obrigatorios: tuple[str, ...] = ()

    def to_internal_value(self, data: Any) -> dict[str, str | list[str]]:
        """Normaliza os parâmetros informados na consulta.

        Args:
            data: Parâmetros recebidos na requisição.

        Returns:
            Parâmetros presentes, como lista ou valor único.
        """
        params: dict[str, str | list[str]] = {}
        if not hasattr(data, "get"):
            return params
        for nome in self.campos_lista:
            valores = data.getlist(nome) if hasattr(data, "getlist") else []
            if valores:
                params[nome] = valores
        for nome in self.campos_simples:
            valor = data.get(nome)
            if valor is not None:
                params[nome] = valor
        return params

    def validate(
        self,
        attrs: dict[str, str | list[str]],
    ) -> dict[str, str | list[str]]:
        """Valida a presença dos parâmetros obrigatórios.

        Args:
            attrs: Parâmetros normalizados.

        Returns:
            Parâmetros validados.

        Raises:
            ValidationError: Quando um parâmetro obrigatório está ausente.
        """
        ausentes = [
            campo for campo in self.campos_obrigatorios if campo not in attrs
        ]
        if ausentes:
            raise serializers.ValidationError(
                dict.fromkeys(ausentes, "Este campo é obrigatório.")
            )
        return attrs


class FuncionariosEscolaCargosQuerySerializer(QueryParamsSerializer):
    """Normaliza filtros de funcionários por cargos na escola."""

    campos_lista = ("cargos",)
    campos_simples = ("dre_codigo",)


class FuncionariosEscolaFuncoesAtividadesQuerySerializer(
    QueryParamsSerializer
):
    """Normaliza filtros de funcionários por funções atividades."""

    campos_lista = ("funcoes_atividades",)
    campos_simples = ("codigo_dre",)


class FuncionariosEscolaFuncoesExternasQuerySerializer(QueryParamsSerializer):
    """Normaliza filtros de funcionários por funções externas."""

    campos_lista = ("funcoes",)
    campos_simples = ("codigo_dre",)
    campos_obrigatorios = ("codigo_dre",)


class ProfessorRfDreUeQuerySerializer(QueryParamsSerializer):
    """Normaliza filtros de professor por RF, DRE e UE."""

    campos_simples = ("dre_id", "ue_id", "buscar_outros_cargos")


class ProfessorAutocompleteQuerySerializer(QueryParamsSerializer):
    """Normaliza filtros de autocomplete de professores."""

    campos_simples = ("ue_id", "nome")


class ProfessorBuscarPorRfQuerySerializer(serializers.Serializer):
    """Normaliza filtros da busca de professor por RF."""

    mensagem_booleano = "buscar_outros_cargos deve ser booleano."

    def to_internal_value(self, data: Any) -> dict[str, bool | None]:
        """Normaliza o filtro de outros cargos.

        Args:
            data: Parâmetros recebidos na requisição.

        Returns:
            Filtro booleano normalizado.

        Raises:
            ValidationError: Quando o valor informado não é booleano.
        """
        valor = (
            data.get("buscar_outros_cargos") if hasattr(data, "get") else None
        )
        if valor is None:
            return {"buscar_outros_cargos": None}
        valor_normalizado = valor.lower()
        if valor_normalizado == "true":
            return {"buscar_outros_cargos": True}
        if valor_normalizado == "false":
            return {"buscar_outros_cargos": False}
        raise serializers.ValidationError(
            {"buscar_outros_cargos": self.mensagem_booleano}
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
        """Retorna código de território saber.

        Args:
            obj: Dados da disciplina.

        Returns:
            Código encontrado quando houver valor.
        """
        return obj.get("codigo_componente_territorio_saber") or None

    def get_tipoEscola(self, obj: dict[str, Any]) -> str | None:  # noqa: N802
        """Retorna tipo de escola.

        Args:
            obj: Dados da disciplina.

        Returns:
            Tipo de escola encontrado.
        """
        return obj.get("tipo_escola")

    def get_professor(self, _obj: dict[str, Any]) -> None:
        """Retorna professor da disciplina.

        Args:
            _obj: Dados da disciplina.

        Returns:
            Valor nulo para o campo.
        """
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
        """Retorna código de território saber.

        Args:
            obj: Dados da disciplina.

        Returns:
            Código encontrado ou zero.
        """
        return obj.get("codigo_componente_territorio_saber") or 0

    def get_tipoEscola(self, _obj: dict[str, Any]) -> None:  # noqa: N802
        """Retorna tipo de escola.

        Args:
            _obj: Dados da disciplina.

        Returns:
            Valor nulo para o campo.
        """
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
        """Retorna tipo de turma.

        Args:
            _obj: Dados da turma.

        Returns:
            Tipo de turma padrão.
        """
        return 0

    def get_dataInicioTurma(self, _obj: Any) -> None:  # noqa: N802
        """Retorna data de início.

        Args:
            _obj: Dados da turma.

        Returns:
            Valor nulo para o campo.
        """
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
        """Retorna o primeiro valor encontrado.

        Args:
            item: Dados usados na busca.
            *campos: Campos consultados em ordem.

        Returns:
            Primeiro valor encontrado.
        """
        for campo in campos:
            valor = item.get(campo)
            if valor is not None:
                return valor
        return None

    def _obter_dre(
        self,
        item: dict[str, Any],
        dres: dict[str, dict[str, Any]],
        codigo_dre: Any,
    ) -> tuple[str, dict[str, Any]]:
        """Retorna a DRE agrupada.

        Args:
            item: Dados usados na composição.
            dres: DREs já agrupadas.
            codigo_dre: Código usado como chave.

        Returns:
            Chave e dados agrupados da DRE.
        """
        chave_dre = str(codigo_dre) if codigo_dre else "__sem_dre__"
        dre = dres.setdefault(
            chave_dre,
            {
                "abreviacao": self._valor(item, "dre_abreviacao", "dre_abrev"),
                "codigo": codigo_dre,
                "nome": item.get("dre"),
                "ues": [],
            },
        )
        return chave_dre, dre

    def _obter_ue(
        self,
        item: dict[str, Any],
        ues_por_dre: dict[tuple[str, str], dict[str, Any]],
        dre: dict[str, Any],
        chave_dre: str,
        codigo_ue: Any,
    ) -> dict[str, Any]:
        """Retorna a UE agrupada.

        Args:
            item: Dados usados na composição.
            ues_por_dre: UEs já agrupadas por DRE.
            dre: Dados agrupados da DRE.
            chave_dre: Chave da DRE.
            codigo_ue: Código usado como chave.

        Returns:
            Dados agrupados da UE.
        """
        chave_ue = (chave_dre, str(codigo_ue))
        ue = ues_por_dre.get(chave_ue)
        if ue is not None:
            return ue

        ue = {
            "codigo": codigo_ue,
            "nome": item.get("ue"),
            "codTipoEscola": self._valor(
                item, "codigo_tipo_escola", "cod_tipo_escola"
            ),
            "turmas": [],
        }
        ues_por_dre[chave_ue] = ue
        cast(list[dict[str, Any]], dre["ues"]).append(ue)
        return ue

    def _montar_turma(
        self,
        item: dict[str, Any],
        codigo_turma: Any,
    ) -> dict[str, Any]:
        """Monta uma turma atribuída.

        Args:
            item: Dados usados na composição.
            codigo_turma: Código da turma.

        Returns:
            Turma no formato de resposta.
        """
        return {
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

    def _ordenar_dres(
        self,
        dres: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Ordena DREs, UEs e turmas.

        Args:
            dres: DREs agrupadas para ordenação.

        Returns:
            DREs ordenadas.
        """
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
        return sorted(
            dres.values(), key=lambda dre: str(dre.get("codigo") or "")
        )

    def to_representation(self, instance: Any) -> Any:
        """Agrupa turmas por DRE e UE.

        Args:
            instance: Dados recebidos para representação.

        Returns:
            Dados agrupados quando houver lista de entrada.
        """
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

            chave_dre, dre = self._obter_dre(item, dres, codigo_dre)
            ue = self._obter_ue(
                item,
                ues_por_dre,
                dre,
                chave_dre,
                codigo_ue,
            )

            codigo_turma = self._valor(item, "codigo_turma", "cod_turma")
            chave_turma = (chave_dre, str(codigo_ue), codigo_turma)
            if chave_turma in turmas_por_ue:
                continue
            turmas_por_ue.add(chave_turma)

            cast(list[dict[str, Any]], ue["turmas"]).append(
                self._montar_turma(item, codigo_turma)
            )

        return {"abrangencia": None, "dres": self._ordenar_dres(dres)}


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
        """Retorna cargo.

        Args:
            _obj: Dados do funcionário.

        Returns:
            Cargo padrão.
        """
        return 0

    def get_codigo_funcao_atividade(self, obj: dict[str, Any]) -> int:
        """Retorna função de atividade.

        Args:
            obj: Dados do funcionário.

        Returns:
            Código da função de atividade.
        """
        return int(obj.get("codigo_funcao_atividade") or 0)


class FuncionarioUeLegadoSerializer(FuncionarioLegadoSerializer):
    """Serializa funcionário por UE no contrato legado."""

    def get_codigo_funcao_atividade(self, _obj: dict[str, Any]) -> int:
        """Retorna função de atividade.

        Args:
            _obj: Dados do funcionário.

        Returns:
            Função de atividade padrão.
        """
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
        """Retorna cargo do vínculo.

        Args:
            obj: Dados do funcionário.

        Returns:
            Código do cargo.
        """
        return int(obj.get("cd_cargo") or obj.get("codigo_cargo") or 0)

    def get_codigoFuncaoAtividade(  # noqa: N802
        self, obj: dict[str, Any]
    ) -> int:
        """Retorna função de atividade.

        Args:
            obj: Dados do funcionário.

        Returns:
            Código da função de atividade.
        """
        return int(obj.get("codigo_funcao_atividade") or 0)


class FuncionarioUnidadeLegadoSerializer(serializers.Serializer):
    """Serializa funcionario por unidade no contrato legado."""

    login = serializers.CharField()
    nomeServidor = serializers.CharField(source="nome_servidor")
    perfil = serializers.CharField()


class FuncionarioDadosSigpaeCargoSerializer(serializers.Serializer):
    """Serializa cargo SIGPAE do funcionario."""

    codigoCargo = serializers.IntegerField(source="codigo_cargo")
    descricaoCargo = serializers.CharField(source="descricao_cargo")
    codigoUnidade = serializers.CharField(source="codigo_unidade")
    descricaoUnidade = serializers.CharField(source="descricao_unidade")
    codigoDre = serializers.CharField(source="codigo_dre")
    contratoExterno = serializers.BooleanField(source="contrato_externo")


class FuncionarioDadosSigpaeSerializer(serializers.Serializer):
    """Serializa dados SIGPAE do funcionario."""

    rf = serializers.CharField()
    cpf = serializers.CharField()
    email = serializers.EmailField(allow_blank=True, allow_null=True)
    cargos = FuncionarioDadosSigpaeCargoSerializer(many=True)
    nome = serializers.CharField()
    inexistenteEol = serializers.BooleanField(source="inexistente_eol")


class ProfessorBuscarPorRfSerializer(serializers.Serializer):
    """Serializa dados resumidos de professor."""

    codigoRF = serializers.CharField(source="codigo_rf")
    nome = serializers.CharField()


class ProfessorEscolaLegadoSerializer(serializers.Serializer):
    """Serializa professor de uma escola no contrato legado."""

    codigoRF = serializers.IntegerField(source="codigo_rf")
    nome = serializers.CharField()
    cargo = serializers.CharField(allow_null=True)
    cpf = serializers.CharField(allow_null=True)
    dataInicioExercicio = serializers.CharField(
        source="data_inicio_exercicio",
        allow_null=True,
    )


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


class CargoFuncionarioConectaSerializer(serializers.Serializer):
    """Serializa cargos por registro funcional."""

    rf = serializers.IntegerField()
    cpf = serializers.CharField(allow_null=True)
    cdCargoBase = serializers.IntegerField(
        source="cd_cargo_base",
        allow_null=True,
    )
    cargoBase = serializers.CharField(source="cargo_base", allow_null=True)
    cdDreCargoBase = serializers.CharField(
        source="cd_dre_cargo_base",
        allow_null=True,
    )
    cdUeCargoBase = serializers.CharField(
        source="cd_ue_cargo_base",
        allow_null=True,
    )
    ueCargoBase = serializers.CharField(
        source="ue_cargo_base",
        allow_null=True,
    )
    tipoVinculoCargoBase = serializers.IntegerField(
        source="tipo_vinculo_cargo_base",
        allow_null=True,
    )
    dataInicioCargoBase = serializers.CharField(
        source="data_inicio_cargo_base",
        allow_null=True,
    )
    cdCargoSobreposto = serializers.IntegerField(
        source="cd_cargo_sobreposto",
        allow_null=True,
    )
    cargoSobreposto = serializers.CharField(
        source="cargo_sobreposto",
        allow_null=True,
    )
    cdDreCargoSobreposto = serializers.CharField(
        source="cd_dre_cargo_sobreposto",
        allow_null=True,
    )
    cdUeCargoSobreposto = serializers.CharField(
        source="cd_ue_cargo_sobreposto",
        allow_null=True,
    )
    ueCargoSobreposto = serializers.CharField(
        source="ue_cargo_sobreposto",
        allow_null=True,
    )
    tipoVinculoCargoSobreposto = serializers.IntegerField(
        source="tipo_vinculo_cargo_sobreposto",
        allow_null=True,
    )
    dataInicioCargoSobreposto = serializers.CharField(
        source="data_inicio_cargo_sobreposto",
        allow_null=True,
    )
    cdFuncaoAtividade = serializers.IntegerField(
        source="cd_funcao_atividade",
        allow_null=True,
    )
    funcaoAtividade = serializers.CharField(
        source="funcao_atividade",
        allow_null=True,
    )
    cdDreFuncaoAtividade = serializers.CharField(
        source="cd_dre_funcao_atividade",
        allow_null=True,
    )
    cdUeFuncaoAtividade = serializers.CharField(
        source="cd_ue_funcao_atividade",
        allow_null=True,
    )
    ueFuncaoAtividade = serializers.CharField(
        source="ue_funcao_atividade",
        allow_null=True,
    )
    tipoVinculoFuncaoAtividade = serializers.IntegerField(
        source="tipo_vinculo_funcao_atividade",
        allow_null=True,
    )
    dataInicioFuncaoAtividade = serializers.CharField(
        source="data_inicio_funcao_atividade",
        allow_null=True,
    )


class FuncionarioConectaFormacaoSerializer(serializers.Serializer):
    """Serializa funcionário do Conecta Formação."""

    rf = serializers.CharField()
    nome = serializers.CharField(allow_null=True)
    cpf = serializers.CharField(allow_null=True)
    cargoCodigo = serializers.CharField(
        source="cargo_codigo",
        allow_null=True,
    )
    cargo = serializers.CharField(allow_null=True)
    cargoDreCodigo = serializers.CharField(
        source="cargo_dre_codigo",
        allow_null=True,
    )
    cargoUeCodigo = serializers.CharField(
        source="cargo_ue_codigo",
        allow_null=True,
    )
    funcaoCodigo = serializers.CharField(
        source="funcao_codigo",
        allow_null=True,
    )
    funcao = serializers.CharField(allow_null=True)
    funcaoDreCodigo = serializers.CharField(
        source="funcao_dre_codigo",
        allow_null=True,
    )
    funcaoUeCodigo = serializers.CharField(
        source="funcao_ue_codigo",
        allow_null=True,
    )
    tipoVinculo = serializers.IntegerField(
        source="tipo_vinculo",
        allow_null=True,
    )


class FuncionariosConectaFormacaoFiltroSerializer(serializers.Serializer):
    """Valida filtros de funcionários do Conecta Formação."""

    codigos_cargos = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    codigos_funcoes = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    codigo_modalidade = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    anos_turma = serializers.ListField(
        child=TextoEstritoField(allow_blank=False),
        required=False,
        allow_empty=True,
        default=list,
    )
    codigos_dres = serializers.ListField(
        child=TextoEstritoField(allow_blank=False),
        required=False,
        allow_empty=True,
        default=list,
    )
    codigos_componentes_curriculares = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    eh_tipo_jornada_jeif = serializers.BooleanField(
        required=False,
        default=False,
    )

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """Preserva parâmetros repetidos recebidos na query.

        Args:
            data: Parâmetros recebidos na requisição.

        Returns:
            Dados normalizados para validação.
        """
        if hasattr(data, "getlist"):
            data = {
                campo: data.getlist(campo)
                for campo in self.fields
                if data.getlist(campo)
            }
            if "eh_tipo_jornada_jeif" in data:
                data["eh_tipo_jornada_jeif"] = data["eh_tipo_jornada_jeif"][0]
        return cast(dict[str, Any], super().to_internal_value(data))


class DreUeAtribuicaoCargoSerializer(serializers.Serializer):
    """Serializa DRE e UE da atribuição por cargo."""

    dreCodigo = serializers.CharField(source="codigo_dre", allow_null=True)
    ueCodigo = serializers.CharField(source="codigo_ue", allow_null=True)


class UsuarioConectaFormacaoSerializer(serializers.Serializer):
    """Serializa usuário do Conecta Formação."""

    login = serializers.CharField()
    nome = serializers.CharField(allow_null=True)
    nomeSocial = serializers.CharField(source="nome_social", allow_null=True)
    perfil = serializers.CharField()


class SupervisorLegadoSerializer(serializers.Serializer):
    """Serializa supervisor no contrato legado."""

    codigoRF = serializers.CharField(source="codigo_rf")
    nomeServidor = serializers.CharField(source="nome_servidor")


class FuncionarioExternoSerializer(serializers.Serializer):
    """Serializa funcionario externo no contrato legado."""

    nomePessoa = serializers.CharField(
        source="nome_pessoa",
        allow_null=True,
        default=None,
    )
    nomePai = serializers.CharField(
        source="nome_pai",
        allow_null=True,
        default=None,
    )
    nomeMae = serializers.CharField(
        source="nome_mae",
        allow_null=True,
        default=None,
    )
    dataNascimento = serializers.CharField(
        source="data_nascimento",
        allow_null=True,
        default=None,
    )
    rg = serializers.CharField(allow_null=True, default=None)
    cpf = serializers.CharField(allow_null=True, default=None)
    tituloEleitoral = serializers.CharField(
        source="titulo_eleitoral",
        allow_null=True,
        default=None,
    )
    pisPasep = serializers.CharField(
        source="pis_pasep",
        allow_null=True,
        default=None,
    )
    codigoContratoExterno = serializers.IntegerField(
        source="codigo_contrato_externo",
        allow_null=True,
        default=None,
    )
    codigoUE = serializers.CharField(
        source="codigo_ue",
        allow_null=True,
        default=None,
    )
    nomeUe = serializers.CharField(
        source="nome_ue",
        allow_null=True,
        default=None,
    )
    funcao = serializers.CharField(allow_null=True, default=None)
    tipoFuncionario = serializers.CharField(
        source="tipo_funcionario",
        allow_null=True,
        default=None,
    )


class FuncionarioLoginSerializer(serializers.Serializer):
    """Serializa funcionario por login no contrato legado."""

    login = serializers.CharField(allow_null=True, default=None)
    nomeServidor = serializers.CharField(
        source="nome_servidor",
        allow_null=True,
        default=None,
    )
    perfil = serializers.CharField(allow_null=True, default=None)


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
        """Retorna login.

        Args:
            _obj: Dados do funcionário.

        Returns:
            Valor nulo para o campo.
        """
        return None

    def get_cd_cargo(self, obj: Any) -> int:
        """Retorna código do cargo.

        Args:
            obj: Dados do funcionário.

        Returns:
            Código do cargo convertido.
        """
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


class VerificarAtribuicaoDisciplinaQuerySerializer(serializers.Serializer):
    """Valida os parâmetros da verificação de atribuição por disciplina."""

    territorioSaber = serializers.BooleanField(
        required=False,
        default=False,
    )


class ProfessorStatusAtribuicaoSerializer(serializers.Serializer):
    """Serializa o status de atribuição do professor em uma turma."""

    anoAtribuicao = serializers.IntegerField(
        source="ano_atribuicao", allow_null=True
    )
    dataCancelamento = serializers.DateField(
        source="data_cancelamento", allow_null=True
    )
    dataDisponibilizacao = serializers.DateField(
        source="data_disponibilizacao", allow_null=True
    )
    dataFimTurma = serializers.DateField(
        source="data_fim_turma", allow_null=True
    )
    codigoMotivoDisponibilizacao = serializers.IntegerField(
        source="codigo_motivo_disponibilizacao", allow_null=True
    )


class ProfessorAtribuicaoTurmaDisciplinaSerializer(serializers.Serializer):
    """Serializa a atribuição do professor em uma turma e disciplina."""

    codigoTurma = serializers.IntegerField(
        source="codigo_turma", allow_null=True
    )
    anoLetivo = serializers.IntegerField(source="ano_letivo", allow_null=True)
    nomeTurma = serializers.CharField(source="nome_turma", allow_null=True)
    dataInicioAtribuicao = serializers.DateField(
        source="data_inicio_atribuicao", allow_null=True
    )
    dataFimAtribuicao = serializers.DateField(
        source="data_fim_atribuicao", allow_null=True
    )
    dataFimTurma = serializers.DateField(
        source="data_fim_turma", allow_null=True
    )
    anoAtribuicao = serializers.IntegerField(
        source="ano_atribuicao", allow_null=True
    )
    codigoRf = serializers.CharField(source="codigo_rf", allow_null=True)
    disciplinaId = serializers.IntegerField(
        source="disciplina_id", allow_null=True
    )
    disciplinaNome = serializers.CharField(
        source="disciplina_nome", allow_null=True
    )
    disciplinasAgrupadasIds = serializers.ListField(
        source="disciplinas_agrupadas_ids",
        child=serializers.IntegerField(),
        allow_null=True,
        allow_empty=True,
        default=list,
    )
    nomeProfessor = serializers.CharField(
        source="nome_professor", allow_null=True
    )


class ProfessorAtribuicaoInternaSerializer(serializers.Serializer):
    """Padroniza atribuições consumidas de diferentes domínios."""

    codigo_turma = serializers.CharField(allow_null=True, default=None)
    ano_letivo = serializers.IntegerField(allow_null=True, default=None)
    nome_turma = serializers.CharField(allow_null=True, default=None)
    data_inicio_atribuicao = serializers.DateTimeField(
        allow_null=True, default=None
    )
    data_fim_atribuicao = serializers.DateTimeField(
        allow_null=True, default=None
    )
    data_fim_turma = serializers.DateTimeField(allow_null=True, default=None)
    ano_atribuicao = serializers.IntegerField(allow_null=True, default=None)
    codigo_rf = serializers.CharField(allow_null=True, default=None)
    disciplina_id = serializers.CharField(allow_null=True, default=None)
    disciplina_nome = serializers.CharField(allow_null=True, default=None)
    disciplinas_agrupadas_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_null=True,
        allow_empty=True,
        default=list,
    )
    nome_professor = serializers.CharField(allow_null=True, default=None)


class ProfessorRecorrenciaDataSerializer(serializers.Serializer):
    """Serializa a permissão de persistência para uma data recorrente."""

    data = serializers.CharField()  # type: ignore[assignment]
    podePersistir = serializers.BooleanField(source="pode_persistir")


class ProfessorAtribuicaoPeriodoPathSerializer(serializers.Serializer):
    """Valida os parâmetros de rota da atribuição por período."""

    codigo_rf = serializers.CharField(allow_blank=False)
    codigo_turma = serializers.CharField(allow_blank=False)
    componente_curricular_id = serializers.CharField(allow_blank=False)
    data_inicio_periodo = serializers.DateTimeField(
        input_formats=["iso-8601", "%Y-%m-%d"]
    )
    data_fim_periodo = serializers.DateTimeField(
        input_formats=["iso-8601", "%Y-%m-%d"]
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Valida a ordem cronológica do período.

        Args:
            attrs: Parâmetros de rota convertidos pelo serializer.

        Returns:
            Parâmetros validados.

        Raises:
            serializers.ValidationError: Quando o período está invertido.
        """
        if attrs["data_inicio_periodo"] > attrs["data_fim_periodo"]:
            raise serializers.ValidationError("Período informado é inválido.")
        return attrs


class ProfessoresTitularesParametrosSerializer(serializers.Serializer):
    """Valida os filtros da busca de professores titulares."""

    codigo_turma = serializers.CharField(allow_blank=False)
    codigoRF = serializers.CharField(
        source="codigo_rf",
        required=False,
        allow_blank=True,
        default="",
    )
    dataReferencia = serializers.DateTimeField(
        source="data_referencia",
        required=False,
        allow_null=True,
        default=None,
        input_formats=["iso-8601", "%Y-%m-%d"],
    )
    realiza_agrupamento = serializers.BooleanField()


class BuscarProfessorTitularPorDisciplinaSerializer(serializers.Serializer):
    """Serializa o professor titular por disciplina no contrato legado."""

    professorRf = serializers.CharField(
        source="professor_rf",
        allow_null=True,
    )
    nome_Professor = serializers.CharField(
        source="nome_professor",
        allow_null=True,
    )
    disciplina = serializers.CharField(allow_null=True)
    disciplina_Id = serializers.CharField(
        source="disciplina_id",
        allow_null=True,
    )
    disciplinas_Id = serializers.CharField(
        source="disciplinas_id",
        allow_null=True,
    )
    turma_Id = serializers.IntegerField(source="turma_id")


class ProfessoresTitularesPorUeParametrosSerializer(serializers.Serializer):
    """Valida os parâmetros da busca de professores titulares por UE."""

    ue_codigo = serializers.CharField(allow_blank=False)
    data_referencia = serializers.DateTimeField(
        input_formats=["iso-8601", "%Y-%m-%d"],
    )
    realizaAgrupamento = serializers.BooleanField(  # noqa: N815
        source="realiza_agrupamento",
        required=False,
        default=False,
    )


class ProfessoresTitularesPorTurmasQuerySerializer(serializers.Serializer):
    """Valida os códigos de turmas da busca de professores titulares."""

    codigosTurmas = serializers.ListField(  # noqa: N815
        source="codigos_turmas",
        child=serializers.CharField(allow_blank=False),
        allow_empty=False,
    )


class ProfessoresTitularesPorTurmasSerializer(
    BuscarProfessorTitularPorDisciplinaSerializer
):
    """Serializa professores titulares de várias turmas."""
