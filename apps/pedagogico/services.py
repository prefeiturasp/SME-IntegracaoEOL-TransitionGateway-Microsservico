"""Serviços do domínio pedagógico."""

from typing import Any

from django.conf import settings

from apps.core.datetime import formatar_datetime_legado
from apps.core.http_client import ServiceClient

_BASE = "/api/v1/pedagogico/componentes-curriculares"
_BASE_TURMAS = "/api/v1/pedagogico/turmas"


_client = ServiceClient(
    base_url=settings.SIDECAR_PEDAGOGICO_URL,
    dominio="pedagogico",
    api_key=settings.SIDECAR_PEDAGOGICO_API_KEY,
    api_key_header=settings.SIDECAR_PEDAGOGICO_API_KEY_HEADER,
)


def get_componentes_curriculares() -> Any:
    """Retorna o catálogo completo de componentes curriculares.

    Returns:
        Catálogo de componentes curriculares ativos.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.get(_BASE).json()


def _codigos_turmas(payload: Any) -> list[str]:
    codigos = []
    for item in payload:
        if isinstance(item, dict):
            codigos.append(str(item["codigo"]))
        else:
            codigos.append(str(item))
    return codigos


def _payload_turmas(response: Any) -> list[str]:
    payload = _client.json_or_none(response)
    if payload is None:
        return []
    return _codigos_turmas(payload)


def _turma_legado(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "ano": item.get("ano"),
        "anoLetivo": item.get("ano_letivo"),
        "codigo": item["codigo"],
        "tipoTurma": item.get("tipo_turma"),
        "modalidade": None,
        "codigoModalidade": 0,
        "nomeTurma": item.get("nome_turma"),
        "semestre": item.get("semestre"),
        "duracaoTurno": item.get("duracao_turno"),
        "tipoTurno": item.get("tipo_turno"),
        "dataFim": formatar_datetime_legado(item.get("data_fim")),
        "ehistorico": item.get("ehistorico", False),
        "ensinoEspecial": item.get("ensino_especial"),
        "etapaEJA": item.get("etapa_eja", 0),
        "serieEnsino": None,
        "dataInicioTurma": formatar_datetime_legado(
            item.get("data_inicio_turma")
        ),
        "extinta": item.get("extinta"),
        "situacao": None,
        "ueCodigo": item.get("ue_codigo"),
    }


def post_turmas_regulares(codigos: list[str]) -> list[str]:
    """Retorna codigos de turmas regulares existentes.

    Args:
        codigos: Codigos das turmas recebidos no contrato legado.

    Returns:
        Codigos das turmas regulares no formato legado.

    Raises:
        httpx.HTTPError: Se a chamada ao servico pedagogico falhar.
        ValueError: Se a resposta nao puder ser convertida para JSON.
    """
    if not codigos:
        return []

    response = _client.post(
        f"{_BASE_TURMAS}/turmas-regulares/",
        payload=[int(codigo) for codigo in codigos],
    )
    return _payload_turmas(response)


def post_turmas_programa(codigos: list[str]) -> list[str]:
    """Retorna codigos de turmas programa existentes.

    Args:
        codigos: Codigos das turmas recebidos no contrato legado.

    Returns:
        Codigos das turmas programa no formato legado.

    Raises:
        httpx.HTTPError: Se a chamada ao servico pedagogico falhar.
        ValueError: Se a resposta nao puder ser convertida para JSON.
    """
    if not codigos:
        return []

    response = _client.post(
        f"{_BASE_TURMAS}/turmas-programa/",
        payload=[int(codigo) for codigo in codigos],
    )
    return _payload_turmas(response)


def post_listar_turmas(codigos: list[str]) -> list[dict[str, Any]]:
    """Retorna dados de turmas existentes.

    Args:
        codigos: Codigos das turmas recebidos no contrato legado.

    Returns:
        Dados das turmas no formato legado.

    Raises:
        httpx.HTTPError: Se a chamada ao servico pedagogico falhar.
        ValueError: Se a resposta nao puder ser convertida para JSON.
    """
    if not codigos:
        return []

    response = _client.post(
        f"{_BASE_TURMAS}/listar-turmas/",
        payload=[int(codigo) for codigo in codigos],
    )
    return [_turma_legado(item) for item in response.json()]


def get_dados_turma(codigo_turma: str) -> dict[str, Any]:
    """Retorna dados de uma turma.

    Args:
        codigo_turma: Codigo da turma recebida no contrato legado.

    Returns:
        Dados da turma no formato legado.

    Raises:
        httpx.HTTPError: Se a chamada ao servico pedagogico falhar.
        ValueError: Se a resposta nao puder ser convertida para JSON.
    """
    response = _client.get(f"{_BASE_TURMAS}/{codigo_turma}/dados/")
    return _turma_legado(response.json())


def get_componentes_por_turmas_ue(
    ue_id: str,
    turmas: list[str],
) -> Any:
    """Retorna componentes curriculares das turmas de uma UE.

    Args:
        ue_id: Código da unidade educacional.
        turmas: Códigos das turmas usadas no filtro.

    Returns:
        Componentes curriculares das turmas informadas.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    params: dict[str, Any] = {"turmas": turmas}

    return _client.get(
        f"{_BASE}/ues/{ue_id}/turmas",
        params=params,
    ).json()


def get_componentes_turmas_programa(
    ue_id: str,
    modalidade: int,
    ano_letivo: int,
) -> Any:
    """Retorna componentes de turmas programa.

    Args:
        ue_id: Código da unidade educacional.
        modalidade: Modalidade de ensino usada no filtro.
        ano_letivo: Ano letivo usado no filtro.

    Returns:
        Componentes das turmas programa encontradas.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.get(
        f"{_BASE}/ues/{ue_id}/modalidades/"
        f"{modalidade}/anos/{ano_letivo}/turmas-programa"
    ).json()


def get_componentes_regencia(ano_turma: int) -> Any:
    """Retorna componentes de regência por ano de turma.

    Args:
        ano_turma: Ano da turma usado na consulta.

    Returns:
        Componentes de regência do ano informado.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.get(f"{_BASE}/anos/{ano_turma}/regencia").json()


def validar_componente_pap(
    codigo_turma: str,
    login: str,
    id_perfil: str,
) -> Any:
    """Verifica se a turma possui componente PAP para o funcionário.

    Args:
        codigo_turma: Código da turma usada na validação.
        login: Login/RF do funcionário.
        id_perfil: Identificador do perfil do funcionário.

    Returns:
        Resultado da validação de componente PAP.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.get(
        f"{_BASE}/turmas/{codigo_turma}/pap",
        params={"login": login, "idPerfil": id_perfil},
    ).json()


def get_componentes_funcionario(login: str, id_perfil: str) -> Any:
    """Retorna componentes curriculares do funcionário.

    Args:
        login: Login/RF do funcionário.
        id_perfil: Identificador do perfil do funcionário.

    Returns:
        Componentes curriculares associados ao funcionário.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.get(
        f"{_BASE}/funcionarios/{login}",
        params={"idPerfil": id_perfil},
    ).json()


def get_componentes_ue_anos(
    ue_id: str,
    modalidade: int,
    ano_letivo: int,
    anos_escolares: list[str],
) -> Any:
    """Retorna componentes filtrados por anos escolares.

    Args:
        ue_id: Código da unidade educacional.
        modalidade: Modalidade de ensino usada no filtro.
        ano_letivo: Ano letivo usado no filtro.
        anos_escolares: Anos escolares usados no filtro.

    Returns:
        Componentes curriculares encontrados para os filtros informados.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    params: dict[str, Any] = {"anos_escolares": anos_escolares}
    path = (
        f"{_BASE}/ues/"
        f"{ue_id}/modalidades/"
        f"{modalidade}/anos/"
        f"{ano_letivo}"
    )
    return _client.get(
        path,
        params=params,
    ).json()


def get_grade_curricular(ano_letivo: int) -> Any:
    """Retorna a grade curricular completa do ano letivo.

    Args:
        ano_letivo: Ano letivo usado na consulta.

    Returns:
        Grade curricular do ano letivo informado.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.get(f"{_BASE}/grade-curricular/{ano_letivo}").json()
