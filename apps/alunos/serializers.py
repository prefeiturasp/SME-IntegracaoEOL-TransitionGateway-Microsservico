"""Serializers de saida para o contrato legado de alunos."""

from typing import Any, cast

from django.utils import timezone
from rest_framework import serializers

from apps.core.datetime import datetime_legado, parse_date
from apps.core.utils import get_first_value, string_or_none

_DATA_PADRAO_LEGADO = "0001-01-01T00:00:00"


class NumeroAlunoChamadaField(serializers.CharField):
    """Serializa número de chamada com fallback legado."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("allow_blank", True)
        kwargs.setdefault("allow_null", True)
        super().__init__(**kwargs)

    def get_attribute(self, instance: Any) -> Any:
        value = super().get_attribute(instance)
        return "0" if value in (None, "") else value

    def to_representation(self, value: Any) -> str:
        return "0" if value in (None, "") else str(value)


def _idade(value: Any) -> int | None:
    """Calcula idade em anos completos.

    Args:
        value: Data de nascimento em formato aceito pelo contrato.

    Returns:
        Idade calculada, ou ``None`` quando não houver data válida.
    """
    nascimento = parse_date(value)
    if nascimento is None:
        return None
    hoje = timezone.now().date()
    idade = hoje.year - nascimento.year
    if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
        idade -= 1
    return cast(int, idade)


def _celular_responsavel(instance: Any) -> str:
    """Monta o celular do responsável.

    Args:
        instance: Dicionário ou objeto com campos de contato.

    Returns:
        Celular já informado ou concatenação de DDD e número.
    """
    celular = get_first_value(
        instance,
        "celular_responsavel",
        "celularResponsavel",
    )
    if celular is not None:
        return str(celular)
    ddd = get_first_value(instance, "ddd_celular", "dddCelular")
    numero = get_first_value(instance, "numero_celular", "numeroCelular")
    if ddd or numero:
        return f"{ddd or ''}{numero or ''}"
    return ""


def _numero_chamada(instance: Any) -> str:
    """Obtém o número de chamada do aluno.

    Args:
        instance: Dicionário ou objeto com os dados da matrícula.

    Returns:
        Número de chamada como string, usando ``"0"`` como fallback.
    """
    value = get_first_value(
        instance,
        "numero_aluno_chamada",
        "numeroAlunoChamada",
    )
    return "0" if value in (None, "") else str(value)


def _endereco_legado(instance: Any) -> dict[str, Any] | None:
    """Normaliza o bloco de endereço para o contrato legado.

    Args:
        instance: Dicionário ou objeto com campo ``endereco``.

    Returns:
        Endereço com chaves legadas, ou o valor original quando não for dict.
    """
    endereco = get_first_value(instance, "endereco")
    if not isinstance(endereco, dict):
        return cast(dict[str, Any] | None, endereco)
    return {
        "id": get_first_value(endereco, "id"),
        "nro": get_first_value(
            endereco,
            "nro",
            "numero_endereco",
            "numeroEndereco",
        ),
        "complemento": get_first_value(endereco, "complemento"),
        "bairro": get_first_value(endereco, "bairro"),
        "cep": get_first_value(endereco, "cep"),
        "nomeMunicipio": get_first_value(
            endereco,
            "nomeMunicipio",
            "nome_municipio",
        ),
        "siglaUF": get_first_value(endereco, "siglaUF", "sigla_uf"),
        "tipologradouro": get_first_value(
            endereco,
            "tipologradouro",
            "tipo_logradouro",
        ),
        "logradouro": get_first_value(endereco, "logradouro"),
    }


class AlunoInformacoesSerializer(serializers.Serializer):
    """Serializa informações cadastrais do aluno."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma dados cadastrais no contrato legado.

        Args:
            instance: Dicionário ou objeto com os dados do aluno.

        Returns:
            Dicionário com os campos cadastrais do aluno.
        """
        return {
            "codigoAluno": get_first_value(
                instance, "codigo_aluno", "codigoAluno"
            ),
            "nomeAluno": get_first_value(instance, "nome_aluno", "nomeAluno"),
            "nomeMae": get_first_value(instance, "nome_mae", "nomeMae"),
            "sexo": get_first_value(instance, "sexo"),
            "grupoEtnico": get_first_value(
                instance,
                "grupo_etnico",
                "grupoEtnico",
                "raca_cor",
                "racaCor",
            ),
            "nacionalidade": get_first_value(instance, "nacionalidade"),
            "endereco": _endereco_legado(instance),
            "ehImigrante": bool(
                get_first_value(
                    instance,
                    "eh_imigrante",
                    "ehImigrante",
                    default=False,
                )
            ),
            "nis": get_first_value(instance, "nis"),
            "cns": get_first_value(instance, "cns"),
        }


class AlunoAutocompleteSerializer(serializers.Serializer):
    """Serializa dados de autocomplete de aluno."""

    codigoAluno = serializers.IntegerField(
        source="codigo_aluno", allow_null=True
    )  # NOSONAR
    nomeAluno = serializers.CharField(
        source="nome_aluno", allow_null=True
    )  # NOSONAR
    nomeSocialAluno = serializers.CharField(
        source="nome_social_aluno", allow_null=True
    )  # NOSONAR
    codigoTurma = serializers.IntegerField(
        source="codigo_turma", allow_null=True
    )  # NOSONAR
    numeroAlunoChamada = NumeroAlunoChamadaField(
        source="numero_aluno_chamada"
    )  # NOSONAR
    turma = serializers.CharField(allow_null=True)
    modalidade = serializers.CharField(allow_null=True)


class InformacoesAlunoTurmaSerializer(serializers.Serializer):
    """Serializa resumo de aluno em turma."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma dados de aluno da turma no contrato legado.

        Args:
            instance: Dicionário ou objeto com dados resumidos do aluno.

        Returns:
            Dicionário com os campos esperados pelo diário/lista de chamada.
        """
        return {
            "numeroChamada": get_first_value(
                instance,
                "numero_chamada",
                "numeroChamada",
            ),
            "codigoAluno": get_first_value(
                instance, "codigo_aluno", "codigoAluno"
            ),
            "nomeAluno": get_first_value(instance, "nome_aluno", "nomeAluno"),
            "nomeSocialAluno": get_first_value(
                instance,
                "nome_social_aluno",
                "nomeSocialAluno",
            ),
            "sexo": get_first_value(instance, "sexo"),
            "raca": get_first_value(instance, "raca", "raca_cor", "racaCor"),
            "codigoRaca": get_first_value(
                instance,
                "codigo_raca",
                "codigoRaca",
            ),
        }


class NecessidadeEspecialSerializer(serializers.Serializer):
    """Serializa necessidade especial do aluno."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma necessidade especial no contrato legado.

        Args:
            instance: Dicionário ou objeto com a necessidade especial.

        Returns:
            Dicionário com necessidade e recurso no formato legado.
        """
        return {
            "codigoAluno": get_first_value(
                instance, "codigo_aluno", "codigoAluno"
            ),
            "tipoNecessidadeEspecial": get_first_value(
                instance,
                "tipo_necessidade_especial",
                "tipoNecessidadeEspecial",
                "codigoNecessidadeEspecial",
            ),
            "descricaoNecessidadeEspecial": get_first_value(
                instance,
                "descricao_necessidade_especial",
                "descricaoNecessidadeEspecial",
                "descricao",
            ),
            "tipoRecurso": get_first_value(
                instance, "tipo_recurso", "tipoRecurso"
            ),
            "descricaoRecurso": get_first_value(
                instance,
                "descricao_recurso",
                "descricaoRecurso",
            ),
        }


class TurmaDoAlunoSerializer(serializers.Serializer):
    """Serializa dados de matrícula e turma do aluno."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma matrícula/turma no contrato legado.

        Args:
            instance: Dicionário ou objeto com dados de matrícula e turma.

        Returns:
            Dicionário com os campos de turma esperados pelo legado.
        """
        data_nascimento = get_first_value(
            instance,
            "data_nascimento",
            "dataNascimento",
        )
        return {
            "codigoAluno": get_first_value(
                instance, "codigo_aluno", "codigoAluno"
            ),
            "anoLetivo": get_first_value(instance, "ano_letivo", "anoLetivo"),
            "nomeAluno": get_first_value(instance, "nome_aluno", "nomeAluno"),
            "nomeSocialAluno": get_first_value(
                instance,
                "nome_social_aluno",
                "nomeSocialAluno",
            ),
            "codigoSituacaoMatricula": get_first_value(
                instance,
                "codigo_situacao_matricula",
                "codigoSituacaoMatricula",
            ),
            "situacaoMatricula": get_first_value(
                instance,
                "situacao_matricula",
                "situacaoMatricula",
            ),
            "dataSituacao": datetime_legado(
                get_first_value(instance, "data_situacao", "dataSituacao")
            ),
            "dataNascimento": datetime_legado(data_nascimento),
            "idade": get_first_value(
                instance, "idade", default=_idade(data_nascimento)
            ),
            "documentoCpf": get_first_value(
                instance,
                "documento_cpf",
                "documentoCpf",
                "cpf",
            ),
            "dataMatricula": datetime_legado(
                get_first_value(instance, "data_matricula", "dataMatricula")
            ),
            "numeroAlunoChamada": _numero_chamada(instance),
            "codigoTurma": get_first_value(
                instance, "codigo_turma", "codigoTurma"
            ),
            "nomeResponsavel": get_first_value(
                instance,
                "nome_responsavel",
                "nomeResponsavel",
            ),
            "tipoResponsavel": string_or_none(
                get_first_value(
                    instance, "tipo_responsavel", "tipoResponsavel"
                )
            ),
            "celularResponsavel": _celular_responsavel(instance),
            "dataAtualizacaoContato": datetime_legado(
                get_first_value(
                    instance,
                    "data_atualizacao_contato",
                    "dataAtualizacaoContato",
                )
            ),
            "codigoEscola": get_first_value(
                instance,
                "codigo_escola",
                "codigoEscola",
                "codigo_ue",
            ),
            "codigoTipoTurma": get_first_value(
                instance,
                "codigo_tipo_turma",
                "codigoTipoTurma",
            ),
            "dataAtualizacaoTabela": datetime_legado(
                get_first_value(
                    instance,
                    "data_atualizacao_tabela",
                    "dataAtualizacaoTabela",
                )
                or get_first_value(instance, "data_situacao", "dataSituacao")
                or _DATA_PADRAO_LEGADO
            ),
        }


class AlunoPorCodigoSerializer(serializers.Serializer):
    """Serializa dados do aluno com campos do contrato de listagem."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma dados do aluno no contrato de listagem legado.

        Args:
            instance: Dicionário ou objeto com dados do aluno e matrícula.

        Returns:
            Dicionário com os campos de listagem do aluno.
        """
        return {
            "codigoAluno": get_first_value(
                instance, "codigo_aluno", "codigoAluno"
            ),
            "tipoTurno": get_first_value(
                instance, "tipo_turno", "tipoTurno", default=0
            ),
            "anoLetivo": get_first_value(instance, "ano_letivo", "anoLetivo"),
            "nomeAluno": get_first_value(instance, "nome_aluno", "nomeAluno"),
            "nomeSocialAluno": get_first_value(
                instance,
                "nome_social_aluno",
                "nomeSocialAluno",
            ),
            "codigoSituacaoMatricula": get_first_value(
                instance,
                "codigo_situacao_matricula",
                "codigoSituacaoMatricula",
            ),
            "situacaoMatricula": get_first_value(
                instance,
                "situacao_matricula",
                "situacaoMatricula",
            ),
            "dataSituacao": datetime_legado(
                get_first_value(instance, "data_situacao", "dataSituacao")
            ),
            "dataNascimento": datetime_legado(
                get_first_value(instance, "data_nascimento", "dataNascimento")
            ),
            "numeroAlunoChamada": _numero_chamada(instance),
            "codigoTurma": get_first_value(
                instance, "codigo_turma", "codigoTurma"
            ),
            "nomeResponsavel": get_first_value(
                instance,
                "nome_responsavel",
                "nomeResponsavel",
            ),
            "tipoResponsavel": string_or_none(
                get_first_value(
                    instance, "tipo_responsavel", "tipoResponsavel"
                )
            ),
            "celularResponsavel": _celular_responsavel(instance),
            "dataAtualizacaoContato": datetime_legado(
                get_first_value(
                    instance,
                    "data_atualizacao_contato",
                    "dataAtualizacaoContato",
                )
            ),
            "codigoTipoTurma": get_first_value(
                instance,
                "codigo_tipo_turma",
                "codigoTipoTurma",
            ),
            "turmaNome": get_first_value(instance, "turma_nome", "turmaNome"),
            "etapaEnsino": get_first_value(
                instance, "etapa_ensino", "etapaEnsino"
            ),
            "cicloEnsino": get_first_value(
                instance, "ciclo_ensino", "cicloEnsino"
            ),
            "descEtapaEnsino": get_first_value(
                instance,
                "desc_etapa_ensino",
                "descEtapaEnsino",
            ),
            "descCicloEnsino": get_first_value(
                instance,
                "desc_ciclo_ensino",
                "descCicloEnsino",
            ),
            "dataAtualizacaoTabela": datetime_legado(
                get_first_value(
                    instance,
                    "data_atualizacao_tabela",
                    "dataAtualizacaoTabela",
                )
                or get_first_value(instance, "data_situacao", "dataSituacao")
                or _DATA_PADRAO_LEGADO
            ),
        }


class ResponsavelResumidoSerializer(serializers.Serializer):
    """Serializa dados resumidos de responsável."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma dados de responsável no contrato legado.

        Args:
            instance: Dicionário ou objeto com dados do responsável.

        Returns:
            Dicionário com os campos resumidos do responsável.
        """
        return {
            "id": get_first_value(instance, "id", "codigo_responsavel"),
            "cpf": get_first_value(instance, "cpf"),
            "email": get_first_value(instance, "email"),
            "nome": get_first_value(instance, "nome"),
            "tipoResponsavel": get_first_value(
                instance,
                "tipo_responsavel",
                "tipoResponsavel",
            ),
            "dataNascimento": datetime_legado(
                get_first_value(instance, "data_nascimento", "dataNascimento")
            ),
            "dataAtualizacao": datetime_legado(
                get_first_value(
                    instance, "data_atualizacao", "dataAtualizacao"
                )
            ),
            "nomeMae": get_first_value(instance, "nome_mae", "nomeMae"),
            "dddCelular": get_first_value(
                instance, "ddd_celular", "dddCelular"
            ),
            "numeroCelular": get_first_value(
                instance,
                "numero_celular",
                "numeroCelular",
            ),
            "codigoAluno": get_first_value(
                instance, "codigo_aluno", "codigoAluno"
            ),
        }
