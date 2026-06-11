"""Serviços do domínio de programas educacionais."""

from typing import Any

from django.conf import settings

from apps.alunos import services as alunos_services
from apps.core.http_client import ServiceClient
from apps.pedagogico import services as pedagogico_services

_BASE = "/api/v1/programasedu/alunos"

_TIPO_TURMA_REGULAR = 1
_TIPO_TURMA_PROGRAMA = 3

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

_client = ServiceClient(
    base_url=settings.SIDECAR_PROGRAMASEDU_URL,
    dominio="programasedu",
    api_key=settings.SIDECAR_PROGRAMASEDU_API_KEY,
    api_key_header=settings.SIDECAR_PROGRAMASEDU_API_KEY_HEADER,
)


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


def listar_alunos_pap_ano_corrente() -> Any:
    """Lista alunos PAP do ano corrente."""
    return _client.get(f"{_BASE}/pap/ano-corrente").json()


def listar_alunos_pap_por_ano(ano_letivo: int) -> Any:
    """Lista alunos PAP do ano letivo informado.

    Args:
        ano_letivo: Ano letivo usado na consulta.

    Returns:
        Alunos PAP do ano letivo informado.
    """
    return _client.get(f"{_BASE}/pap/ano-letivo/{ano_letivo}").json()


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

    1. Alunos-MS retorna turmas do aluno e ``codigo_tipo_turma``.
    2. ProgramasEdu-MS retorna turmas com o componente SRM 1030.
    3. Filtro: mantém turma regular (tipo 1) OU programa (tipo 3) que esteja
       no conjunto SRM.
    4. Pedagogico-MS → ``nome_turma``/``tipo_turno``/etapa/ciclo por turma.

    Args:
        codigo_aluno: Código EOL do aluno.

    Returns:
        Lista de dicts (snake_case) prontos para o
        ``TurmaSrmRegularDoAlunoSerializer``.
    """
    turmas_aluno = (
        alunos_services.get_turmas_aluno_com_programa(codigo_aluno) or []
    )
    if not turmas_aluno:
        return []

    dados_srm = obter_dados_srm_paee_aluno(codigo_aluno) or []
    codigos_srm = {item.get("codigo_turma") for item in dados_srm}

    selecionadas = [
        t
        for t in turmas_aluno
        if t.get("codigo_tipo_turma") == _TIPO_TURMA_REGULAR
        or (
            t.get("codigo_tipo_turma") == _TIPO_TURMA_PROGRAMA
            and t.get("codigo_turma") in codigos_srm
        )
    ]
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
