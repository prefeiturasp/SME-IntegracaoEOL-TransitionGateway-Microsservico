"""Serviços do domínio de programas educacionais."""

import gzip
import json
import logging
from typing import Any

from django.utils import timezone
from rest_framework.renderers import JSONRenderer

from apps.alunos import services as alunos_services
from apps.core import cache
from apps.core.api_clients import get_api_client
from apps.pedagogico import services as pedagogico_services
from apps.programasedu.serializers import AlunoTurmaPapSerializer

logger = logging.getLogger(__name__)

_BASE = "/api/v1/programasedu/alunos"


_DESC_ETAPA_ENSINO = {
    1: "EI",
    2: "CIEJA",
    3: "EJA",
    4: "FUND8A",
    5: "FUND9A",
    6: "EM",
    7: "EMEJA",
    8: "EMI",
    9: "MAG",
    10: "EIESP",
    11: "EJAESP",
    12: "FUND8AESP",
    13: "FUND9AESP",
    14: "EMTEC",
    16: "PROJ",
    17: "EMESP",
}

_client = get_api_client("programasedu")


def listar_turmas_pap(ano_letivo: int, codigo_escola: str) -> Any:
    """Lista turmas PAP da UE no ano letivo.

    Args:
        ano_letivo: Ano letivo usado na consulta.
        codigo_escola: Código da unidade educacional.

    Returns:
        Turmas PAP encontradas para a unidade educacional.
    """
    return _client.get(
        f"{_BASE}/turmas-pap/{ano_letivo}/ues/{codigo_escola}"
    ).json()


def verificar_alunos_pap(ano_letivo: int, codigos_alunos: list[str]) -> Any:
    """Verifica alunos vinculados a turmas PAP no ano letivo.

    Args:
        ano_letivo: Ano letivo usado na consulta.
        codigos_alunos: Códigos dos alunos verificados.

    Returns:
        Alunos encontrados em turmas PAP.
    """
    params: dict[str, Any] = {"codigos_alunos": codigos_alunos}
    return _client.get(
        f"{_BASE}/alunos-pap/{ano_letivo}", params=params
    ).json()


# Nomes dos campos emitidos pelo serviço de programas e seus equivalentes no
# contrato público. A troca é feita sobre os bytes para não materializar
# centenas de milhares de linhas em objetos Python.
_CAMPOS_ALUNO_PAP = (
    (b'"ano_letivo":', b'"anoLetivo":'),
    (b'"codigo_turma":', b'"codigoTurma":'),
    (b'"codigo_ue":', b'"codigoUe":'),
    (b'"codigo_dre":', b'"codigoDre":'),
    (b'"codigo_aluno":', b'"codigoAluno":'),
    (b'"componente_curricular_id":', b'"componenteCurricularId":'),
)
_PREFIXO_CACHE_ALUNOS_PAP = "programasedu:alunos-pap:v1"
_MAGIA_GZIP = bytes((0x1F, 0x8B))
_TTL_ALUNOS_PAP_ANO_CORRENTE = cache.TTL_RECOMENDADO_MINUTOS
_TTL_ALUNOS_PAP_ANO_ENCERRADO = cache.TTL_LEGADO_PADRAO_MINUTOS


def _traduzir_alunos_pap(corpo: bytes) -> bytes:
    """Traduz o JSON de alunos PAP para os nomes do contrato público.

    Args:
        corpo: Array JSON devolvido pelo serviço de programas.

    Returns:
        Array JSON com os campos no formato do contrato público.
    """
    traduzido = corpo
    for origem, destino in _CAMPOS_ALUNO_PAP:
        traduzido = traduzido.replace(origem, destino)
    if any(origem[:-1] in traduzido for origem, _ in _CAMPOS_ALUNO_PAP):
        logger.warning("Formato inesperado de alunos PAP; usando serializer")
        return bytes(
            JSONRenderer().render(
                AlunoTurmaPapSerializer(json.loads(corpo), many=True).data
            )
        )
    return traduzido


def _buscar_alunos_pap_comprimido(caminho: str) -> bytes:
    """Busca alunos PAP no serviço de programas e devolve JSON em gzip.

    Args:
        caminho: Caminho da consulta no serviço de programas.

    Returns:
        Array JSON do contrato público comprimido em gzip.

    Raises:
        httpx.HTTPError: Em caso de falha de transporte ou resposta de erro.
    """
    resposta = _client.get(caminho)
    resposta.raise_for_status()
    return gzip.compress(_traduzir_alunos_pap(resposta.content), 1, mtime=0)


def _alunos_pap_em_cache(
    chave: str, caminho: str, minutos_para_expirar: int
) -> bytes:
    """Obtém o gzip de alunos PAP do cache ou do serviço de programas.

    Args:
        chave: Chave de cache da consulta.
        caminho: Caminho da consulta no serviço de programas.
        minutos_para_expirar: Tempo de vida do valor em cache.

    Returns:
        Array JSON do contrato público comprimido em gzip.
    """

    def buscar() -> bytes:
        return _buscar_alunos_pap_comprimido(caminho)

    armazenado = cache.obter_ou_calcular(chave, buscar, minutos_para_expirar)
    if isinstance(armazenado, bytes) and armazenado[:2] == _MAGIA_GZIP:
        return armazenado
    logger.warning("Alunos PAP armazenados em formato inválido")
    return buscar()


def listar_alunos_pap_ano_corrente() -> bytes:
    """Lista alunos PAP do ano corrente.

    Returns:
        Array JSON do contrato público comprimido em gzip.
    """
    ano = timezone.now().year
    return _alunos_pap_em_cache(
        f"{_PREFIXO_CACHE_ALUNOS_PAP}:ano-corrente:{ano}",
        f"{_BASE}/pap/ano-corrente",
        _TTL_ALUNOS_PAP_ANO_CORRENTE,
    )


def listar_alunos_pap_por_ano(ano_letivo: int) -> bytes:
    """Lista alunos PAP do ano letivo informado.

    Args:
        ano_letivo: Ano letivo usado na consulta.

    Returns:
        Array JSON do contrato público comprimido em gzip. Anos corrente e
        futuros não são armazenados em cache.
    """
    caminho = f"{_BASE}/pap/ano-letivo/{ano_letivo}"
    if ano_letivo >= timezone.now().year:
        return _buscar_alunos_pap_comprimido(caminho)
    return _alunos_pap_em_cache(
        f"{_PREFIXO_CACHE_ALUNOS_PAP}:ano-letivo:{ano_letivo}",
        caminho,
        _TTL_ALUNOS_PAP_ANO_ENCERRADO,
    )


def listar_componentes_turmas_programa_aluno(
    codigo_aluno: str, ano_letivo: int
) -> Any:
    """Lista componentes curriculares das turmas de programa do aluno.

    Args:
        codigo_aluno: Código do aluno consultado.
        ano_letivo: Ano letivo usado na consulta.

    Returns:
        Componentes curriculares das turmas de programa do aluno.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_aluno}/turmas-programa/{ano_letivo}"
        "/componentes-curriculares"
    )
    return _client.json_or_none(resp) or []


def obter_dados_srm_paee_aluno(codigo_aluno: str) -> Any:
    """Retorna dados de SRM/PAEE colaborativo do aluno.

    Args:
        codigo_aluno: Código do aluno consultado.

    Returns:
        Dados de SRM/PAEE colaborativo do aluno.
    """
    resp = _client.get(f"{_BASE}/srm-paee/aluno/{codigo_aluno}")
    return _client.json_or_none(resp) or []


def obter_turma_srm_e_regular_do_aluno(codigo_aluno: str) -> list[dict]:
    """Compõe as turmas SRM e regulares do aluno no shape legado.

    Args:
        codigo_aluno: Código EOL do aluno.

    Returns:
        Lista de dicts (snake_case) prontos para o
        ``TurmaSrmRegularDoAlunoSerializer``.
    """
    dados_srm = obter_dados_srm_paee_aluno(codigo_aluno) or []
    codigos_srm = sorted(
        {
            item["codigo_turma"]
            for item in dados_srm
            if item.get("codigo_turma") is not None
        }
    )

    selecionadas = (
        alunos_services.get_turmas_srm_regular_aluno(codigo_aluno, codigos_srm)
        or []
    )
    if not selecionadas:
        return []

    codigos = list({t.get("codigo_turma") for t in selecionadas})
    turmas_ped = pedagogico_services.listar_turmas(codigos) or []
    ped_por_codigo = {tp.get("codigo"): tp for tp in turmas_ped}

    saida: list[dict] = []
    for t in selecionadas:
        tp = ped_por_codigo.get(t.get("codigo_turma"), {})
        etapa = tp.get("codigo_etapa_ensino")
        ddd = t.get("ddd_celular") or ""
        numero = t.get("numero_celular") or ""
        # ausente/'NULL' vira "000"; valor real passa sem alteração.
        numero_chamada = t.get("numero_aluno_chamada")
        if numero_chamada is None or str(numero_chamada).strip().upper() in (
            "",
            "NULL",
        ):
            numero_chamada = "000"
        saida.append(
            {
                "codigo_aluno": t.get("codigo_aluno"),
                "tipo_turno": tp.get("tipo_turno"),
                "ano_letivo": t.get("ano_letivo"),
                "nome_aluno": t.get("nome_aluno"),
                "nome_social_aluno": t.get("nome_social_aluno"),
                "codigo_situacao_matricula": t.get(
                    "codigo_situacao_matricula"
                ),
                "situacao_matricula": t.get("situacao_matricula"),
                "data_situacao": t.get("data_situacao"),
                "data_nascimento": t.get("data_nascimento"),
                "numero_aluno_chamada": numero_chamada,
                "codigo_turma": t.get("codigo_turma"),
                "nome_responsavel": t.get("nome_responsavel"),
                "tipo_responsavel": t.get("tipo_responsavel"),
                "celular_responsavel": f"{ddd}{numero}",
                "data_atualizacao_contato": t.get("data_atualizacao_contato"),
                "codigo_tipo_turma": t.get("codigo_tipo_turma"),
                "turma_nome": tp.get("nome_turma"),
                "etapa_ensino": etapa,
                "ciclo_ensino": tp.get("codigo_ciclo_ensino"),
                "desc_etapa_ensino": _DESC_ETAPA_ENSINO.get(etapa),
                "desc_ciclo_ensino": None,
                "data_atualizacao_tabela": "0001-01-01T00:00:00",
            }
        )
    return saida
