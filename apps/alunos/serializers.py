"""Serializers de saida para o contrato legado de alunos."""

from datetime import date, datetime
from typing import Any, cast
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework import serializers

_DATA_PADRAO_LEGADO = "0001-01-01T00:00:00"
_TZ_LEGADO = ZoneInfo("America/Sao_Paulo")


def _get(instance: Any, *keys: str, default: Any = None) -> Any:
    """Lê o primeiro campo disponível na instância.

    Args:
        instance: Dicionário ou objeto de origem.
        *keys: Chaves consultadas em ordem de prioridade.
        default: Valor retornado quando nenhuma chave existir.

    Returns:
        Valor encontrado ou ``default``.
    """
    if isinstance(instance, dict):
        for key in keys:
            if key in instance:
                return instance[key]
    return default


def _parse_date(value: Any) -> date | None:
    """Transforma valor em ``date``.

    Args:
        value: Valor bruto em ``str``, ``datetime`` ou ``date``.

    Returns:
        Data normalizada, ou ``None`` quando o valor for inválido.
    """
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        raw = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(raw).date()
        except ValueError:
            try:
                return date.fromisoformat(value[:10])
            except ValueError:
                return None
    return None


def _datetime_legado(value: Any) -> str | None:
    """Formata data/hora no padrão ISO esperado pelo legado.

    Args:
        value: Valor bruto em ``str``, ``datetime`` ou ``date``.

    Returns:
        Data/hora sem timezone e sem zeros excedentes na fração.
    """
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return _normalizar_datetime(value.isoformat())
    if isinstance(value, date):
        return f"{value.isoformat()}T00:00:00"
    if isinstance(value, str):
        valor = value.strip().replace(" ", "T", 1)
        if "T" not in valor:
            return f"{valor}T00:00:00"
        return _normalizar_datetime(valor)
    return None


def _normalizar_datetime(value: str) -> str:
    """Normaliza string ISO datetime para o padrão legado.

    Args:
        value: String ISO de data/hora.

    Returns:
        String em horário local, sem timezone e sem zeros excedentes.
    """
    valor_parse = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(valor_parse)
    except ValueError:
        parsed = None

    if parsed is not None:
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(_TZ_LEGADO).replace(tzinfo=None)
        valor = parsed.isoformat()
    else:
        valor = value.replace("Z", "")

    for sep in ("+", "-"):
        pos = valor.find(sep, 10)
        if pos > -1:
            valor = valor[:pos]
            break
    if "." not in valor:
        return valor
    base, frac = valor.split(".", 1)
    frac = frac.rstrip("0")
    return base if not frac else f"{base}.{frac}"


def _idade(value: Any) -> int | None:
    """Calcula idade em anos completos.

    Args:
        value: Data de nascimento em formato aceito por ``_parse_date``.

    Returns:
        Idade calculada, ou ``None`` quando não houver data válida.
    """
    nascimento = _parse_date(value)
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
    celular = _get(instance, "celular_responsavel", "celularResponsavel")
    if celular is not None:
        return str(celular)
    ddd = _get(instance, "ddd_celular", "dddCelular")
    numero = _get(instance, "numero_celular", "numeroCelular")
    if ddd or numero:
        return f"{ddd or ''}{numero or ''}"
    return ""


def _string_or_none(value: Any) -> str | None:
    """Transforma valor em string quando houver conteúdo.

    Args:
        value: Valor bruto.

    Returns:
        String convertida, ou ``None`` para valores vazios.
    """
    if value in (None, ""):
        return None
    return str(value)


def _numero_chamada(instance: Any) -> str:
    """Obtém o número de chamada do aluno.

    Args:
        instance: Dicionário ou objeto com os dados da matrícula.

    Returns:
        Número de chamada como string, usando ``"0"`` como fallback.
    """
    value = _get(instance, "numero_aluno_chamada", "numeroAlunoChamada")
    return "0" if value in (None, "") else str(value)


def _endereco_legado(instance: Any) -> dict[str, Any] | None:
    """Normaliza o bloco de endereço para o contrato legado.

    Args:
        instance: Dicionário ou objeto com campo ``endereco``.

    Returns:
        Endereço com chaves legadas, ou o valor original quando não for dict.
    """
    endereco = _get(instance, "endereco")
    if not isinstance(endereco, dict):
        return cast(dict[str, Any] | None, endereco)
    return {
        "id": _get(endereco, "id"),
        "nro": _get(endereco, "nro", "numero_endereco", "numeroEndereco"),
        "complemento": _get(endereco, "complemento"),
        "bairro": _get(endereco, "bairro"),
        "cep": _get(endereco, "cep"),
        "nomeMunicipio": _get(
            endereco,
            "nomeMunicipio",
            "nome_municipio",
        ),
        "siglaUF": _get(endereco, "siglaUF", "sigla_uf"),
        "tipologradouro": _get(
            endereco,
            "tipologradouro",
            "tipo_logradouro",
        ),
        "logradouro": _get(endereco, "logradouro"),
    }


class AlunoInformacoesSerializer(serializers.Serializer):
    """Serializa informações cadastrais do aluno."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma dados cadastrais no contrato legado.

        Args:
            instance: Dicionário ou objeto com os dados do aluno.

        Returns:
            Dicionário com os campos esperados pelo endpoint legado.
        """
        return {
            "codigoAluno": _get(instance, "codigo_aluno", "codigoAluno"),
            "nomeAluno": _get(instance, "nome_aluno", "nomeAluno"),
            "nomeMae": _get(instance, "nome_mae", "nomeMae"),
            "sexo": _get(instance, "sexo"),
            "grupoEtnico": _get(
                instance,
                "grupo_etnico",
                "grupoEtnico",
                "raca_cor",
                "racaCor",
            ),
            "nacionalidade": _get(instance, "nacionalidade"),
            "endereco": _endereco_legado(instance),
            "ehImigrante": bool(
                _get(
                    instance,
                    "eh_imigrante",
                    "ehImigrante",
                    default=False,
                )
            ),
            "nis": _get(instance, "nis"),
            "cns": _get(instance, "cns"),
        }


class AlunoAutocompleteSerializer(serializers.Serializer):
    """Serializa dados de autocomplete de aluno."""

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Transforma dados de aluno no contrato de autocomplete.

        Args:
            instance: Dicionário ou objeto com dados do aluno e turma.

        Returns:
            Dicionário com os campos esperados pelo autocomplete legado.
        """
        return {
            "codigoAluno": _get(instance, "codigo_aluno", "codigoAluno"),
            "nomeAluno": _get(instance, "nome_aluno", "nomeAluno"),
            "nomeSocialAluno": _get(
                instance,
                "nome_social_aluno",
                "nomeSocialAluno",
            ),
            "codigoTurma": _get(instance, "codigo_turma", "codigoTurma"),
            "numeroAlunoChamada": _numero_chamada(instance),
            "turma": _get(instance, "turma"),
            "modalidade": _get(instance, "modalidade"),
        }


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
            "numeroChamada": _get(
                instance,
                "numero_chamada",
                "numeroChamada",
            ),
            "codigoAluno": _get(instance, "codigo_aluno", "codigoAluno"),
            "nomeAluno": _get(instance, "nome_aluno", "nomeAluno"),
            "nomeSocialAluno": _get(
                instance,
                "nome_social_aluno",
                "nomeSocialAluno",
            ),
            "sexo": _get(instance, "sexo"),
            "raca": _get(instance, "raca", "raca_cor", "racaCor"),
            "codigoRaca": _get(
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
            "codigoAluno": _get(instance, "codigo_aluno", "codigoAluno"),
            "tipoNecessidadeEspecial": _get(
                instance,
                "tipo_necessidade_especial",
                "tipoNecessidadeEspecial",
                "codigoNecessidadeEspecial",
            ),
            "descricaoNecessidadeEspecial": _get(
                instance,
                "descricao_necessidade_especial",
                "descricaoNecessidadeEspecial",
                "descricao",
            ),
            "tipoRecurso": _get(instance, "tipo_recurso", "tipoRecurso"),
            "descricaoRecurso": _get(
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
        data_nascimento = _get(
            instance,
            "data_nascimento",
            "dataNascimento",
        )
        return {
            "codigoAluno": _get(instance, "codigo_aluno", "codigoAluno"),
            "anoLetivo": _get(instance, "ano_letivo", "anoLetivo"),
            "nomeAluno": _get(instance, "nome_aluno", "nomeAluno"),
            "nomeSocialAluno": _get(
                instance,
                "nome_social_aluno",
                "nomeSocialAluno",
            ),
            "codigoSituacaoMatricula": _get(
                instance,
                "codigo_situacao_matricula",
                "codigoSituacaoMatricula",
            ),
            "situacaoMatricula": _get(
                instance,
                "situacao_matricula",
                "situacaoMatricula",
            ),
            "dataSituacao": _datetime_legado(
                _get(instance, "data_situacao", "dataSituacao")
            ),
            "dataNascimento": _datetime_legado(data_nascimento),
            "idade": _get(instance, "idade", default=_idade(data_nascimento)),
            "documentoCpf": _get(
                instance,
                "documento_cpf",
                "documentoCpf",
                "cpf",
            ),
            "dataMatricula": _datetime_legado(
                _get(instance, "data_matricula", "dataMatricula")
            ),
            "numeroAlunoChamada": _numero_chamada(instance),
            "codigoTurma": _get(instance, "codigo_turma", "codigoTurma"),
            "nomeResponsavel": _get(
                instance,
                "nome_responsavel",
                "nomeResponsavel",
            ),
            "tipoResponsavel": _string_or_none(
                _get(instance, "tipo_responsavel", "tipoResponsavel")
            ),
            "celularResponsavel": _celular_responsavel(instance),
            "dataAtualizacaoContato": _datetime_legado(
                _get(
                    instance,
                    "data_atualizacao_contato",
                    "dataAtualizacaoContato",
                )
            ),
            "codigoEscola": _get(
                instance,
                "codigo_escola",
                "codigoEscola",
                "codigo_ue",
            ),
            "codigoTipoTurma": _get(
                instance,
                "codigo_tipo_turma",
                "codigoTipoTurma",
            ),
            "dataAtualizacaoTabela": _datetime_legado(
                _get(
                    instance,
                    "data_atualizacao_tabela",
                    "dataAtualizacaoTabela",
                )
                or _get(instance, "data_situacao", "dataSituacao")
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
            Dicionário com os campos esperados em ``/alunos/alunos``.
        """
        return {
            "codigoAluno": _get(instance, "codigo_aluno", "codigoAluno"),
            "tipoTurno": _get(instance, "tipo_turno", "tipoTurno", default=0),
            "anoLetivo": _get(instance, "ano_letivo", "anoLetivo"),
            "nomeAluno": _get(instance, "nome_aluno", "nomeAluno"),
            "nomeSocialAluno": _get(
                instance,
                "nome_social_aluno",
                "nomeSocialAluno",
            ),
            "codigoSituacaoMatricula": _get(
                instance,
                "codigo_situacao_matricula",
                "codigoSituacaoMatricula",
            ),
            "situacaoMatricula": _get(
                instance,
                "situacao_matricula",
                "situacaoMatricula",
            ),
            "dataSituacao": _datetime_legado(
                _get(instance, "data_situacao", "dataSituacao")
            ),
            "dataNascimento": _datetime_legado(
                _get(instance, "data_nascimento", "dataNascimento")
            ),
            "numeroAlunoChamada": _numero_chamada(instance),
            "codigoTurma": _get(instance, "codigo_turma", "codigoTurma"),
            "nomeResponsavel": _get(
                instance,
                "nome_responsavel",
                "nomeResponsavel",
            ),
            "tipoResponsavel": _string_or_none(
                _get(instance, "tipo_responsavel", "tipoResponsavel")
            ),
            "celularResponsavel": _celular_responsavel(instance),
            "dataAtualizacaoContato": _datetime_legado(
                _get(
                    instance,
                    "data_atualizacao_contato",
                    "dataAtualizacaoContato",
                )
            ),
            "codigoTipoTurma": _get(
                instance,
                "codigo_tipo_turma",
                "codigoTipoTurma",
            ),
            "turmaNome": _get(instance, "turma_nome", "turmaNome"),
            "etapaEnsino": _get(instance, "etapa_ensino", "etapaEnsino"),
            "cicloEnsino": _get(instance, "ciclo_ensino", "cicloEnsino"),
            "descEtapaEnsino": _get(
                instance,
                "desc_etapa_ensino",
                "descEtapaEnsino",
            ),
            "descCicloEnsino": _get(
                instance,
                "desc_ciclo_ensino",
                "descCicloEnsino",
            ),
            "dataAtualizacaoTabela": _datetime_legado(
                _get(
                    instance,
                    "data_atualizacao_tabela",
                    "dataAtualizacaoTabela",
                )
                or _get(instance, "data_situacao", "dataSituacao")
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
            "id": _get(instance, "id", "codigo_responsavel"),
            "cpf": _get(instance, "cpf"),
            "email": _get(instance, "email"),
            "nome": _get(instance, "nome"),
            "tipoResponsavel": _get(
                instance,
                "tipo_responsavel",
                "tipoResponsavel",
            ),
            "dataNascimento": _datetime_legado(
                _get(instance, "data_nascimento", "dataNascimento")
            ),
            "dataAtualizacao": _datetime_legado(
                _get(instance, "data_atualizacao", "dataAtualizacao")
            ),
            "nomeMae": _get(instance, "nome_mae", "nomeMae"),
            "dddCelular": _get(instance, "ddd_celular", "dddCelular"),
            "numeroCelular": _get(
                instance,
                "numero_celular",
                "numeroCelular",
            ),
            "codigoAluno": _get(instance, "codigo_aluno", "codigoAluno"),
        }
