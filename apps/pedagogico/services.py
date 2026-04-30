"""Chamadas ao sidecar pedagógico, uma função por endpoint canônico."""

from typing import Any

from django.conf import settings

from apps.core.http_client import ServiceClient

_BASE = "/api/v1/componentes-curriculares"

_client = ServiceClient(
    base_url=settings.SIDECAR_PEDAGOGICO_URL,
    dominio="pedagogico",
    api_key=settings.SIDECAR_PEDAGOGICO_API_KEY,
    api_key_header=settings.SIDECAR_PEDAGOGICO_API_KEY_HEADER,
)


# EP-1 (legado 1,2,3)
def get_componentes_funcionario(
    login: str,
    id_perfil: str,
    codigo_turma: str | None = None,
    agrupa: bool = False,
    planejamento: bool = False,
    checa_motivo_disponibilizacao: bool = True,
    considera_turma_infantil: bool = True,
) -> Any:
    """Quando codigo_turma é omitido, params de turma não são enviados."""
    params: dict[str, Any] = {"idPerfil": id_perfil}
    if codigo_turma:
        params["codigoTurma"] = codigo_turma
        params["agrupaComponenteCurricular"] = agrupa
        params["planejamento"] = planejamento
        params["checaMotivoDisponibilizacao"] = checa_motivo_disponibilizacao
        params["consideraTurmaInfantil"] = considera_turma_infantil
    return _client.get(f"{_BASE}/funcionarios/{login}", params=params).json()


# EP-2
def get_componentes_regencia(ano_turma: int) -> Any:
    """EP-2. Componentes de regência para o ano de turma."""
    return _client.get(f"{_BASE}/anos/{ano_turma}/regencia").json()


# EP-3
def validar_pap(codigo_turma: str, login: str, id_perfil: str) -> Any:
    """EP-3. Verifica presença de componente PAP na turma."""
    params = {"login": login, "idPerfil": id_perfil}
    return _client.get(
        f"{_BASE}/turmas/{codigo_turma}/pap", params=params
    ).json()


# EP-4
def get_componentes_ue_anos(
    ue_id: str,
    modalidade: int,
    ano_letivo: int,
    anos_escolares: list[str],
) -> Any:
    """EP-4. Componentes filtrados por UE, modalidade, ano e anos escolares."""
    params: dict[str, Any] = {"anosEscolares": anos_escolares}
    return _client.get(
        f"{_BASE}/ues/{ue_id}/modalidades/{modalidade}/anos/{ano_letivo}",
        params=params,
    ).json()


# EP-5
def get_componentes_turmas_programa(
    ue_id: str, modalidade: int, ano_letivo: int
) -> Any:
    """EP-5. Componentes de turmas programa (projetos especiais) da UE."""
    return _client.get(
        f"{_BASE}/ues/{ue_id}/modalidades/{modalidade}/anos/{ano_letivo}/turmas-programa"
    ).json()


# EP-6
def get_componentes_por_turmas_ue(ue_id: str, turmas: list[str]) -> Any:
    """EP-6. Componentes das turmas informadas consolidados por UE."""
    params: dict[str, Any] = {"turmas": turmas}
    return _client.get(f"{_BASE}/ues/{ue_id}/turmas", params=params).json()


# EP-7
def get_componentes_planejamento(
    codigo_turmas: list[str], adicionar_planejamento: bool = True
) -> Any:
    """EP-7. Componentes de múltiplas turmas com expansão de planejamento."""
    params: dict[str, Any] = {
        "codigoTurmas": codigo_turmas,
        "adicionarComponentesPlanejamento": adicionar_planejamento,
    }
    return _client.get(f"{_BASE}/turmas", params=params).json()


# EP-8
def get_componentes_brutos(codigo_turmas: list[str]) -> Any:
    """EP-8. Componentes sem pós-processamento de Território do Saber."""
    params: dict[str, Any] = {"codigoTurmas": codigo_turmas}
    return _client.get(f"{_BASE}/turmas/brutos", params=params).json()


# EP-9
def get_catalogo_componentes() -> Any:
    """EP-9. Todos os componentes curriculares ativos do EOL."""
    return _client.get(_BASE).json()


# EP-10
def get_vigencia_componentes(
    ue_codigo: str | None,
    ano_letivo: str | None,
    componentes: list[str],
    semestre: str | None = None,
) -> Any:
    """Semestre só incluído quando fornecido; filtra EJA/CIEJA."""
    params: dict[str, Any] = {
        "ueCodigo": ue_codigo,
        "anoLetivo": ano_letivo,
        "componentesCurriculares": componentes,
    }
    if semestre:
        params["semestre"] = semestre
    return _client.get(f"{_BASE}/turmas/vigencia", params=params).json()


# EP-11
def get_grade_curricular(ano_letivo: int) -> Any:
    """EP-11. Grade curricular completa do ano letivo."""
    return _client.get(f"{_BASE}/grade-curricular/{ano_letivo}").json()


# EP-12
def get_sem_atribuicao(codigo_turma: str, data_base_tick: str) -> Any:
    """EP-12. Componentes sem professor atribuído na data (ticks .NET)."""
    params = {"dataBase": data_base_tick}
    return _client.get(
        f"{_BASE}/turmas/{codigo_turma}/sem-atribuicao", params=params
    ).json()


# EP-13
def get_agrupamentos_correlacionados(
    codigo: int, data_base: str | None = None
) -> Any:
    """data_base em ticks .NET; ausente = sem filtro de data."""
    params: dict[str, str] = {}
    if data_base:
        params["dataBase"] = data_base
    return _client.get(
        f"{_BASE}/{codigo}/territorio-saber/agrupamentos-correlacionados",
        params=params or None,
    ).json()


# EP-14
def get_agrupamentos_correlacionados_lote(
    ids: list[int], data_base: str | None = None
) -> Any:
    """EP-14. Versão em lote do EP-13; data_base em ticks .NET."""
    params: dict[str, str] = {}
    if data_base:
        params["dataBase"] = data_base
    return _client.post(
        f"{_BASE}/territorio-saber/agrupamentos-correlacionados",
        payload=ids,
        params=params or None,
    ).json()


# EP-15
def get_agrupamentos(ids: list[int]) -> Any:
    """EP-15. Agrupamentos de Território do Saber pelos IDs informados."""
    return _client.post(
        f"{_BASE}/territorio-saber/agrupamentos",
        payload=ids,
    ).json()
