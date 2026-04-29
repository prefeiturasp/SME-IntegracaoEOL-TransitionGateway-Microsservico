from django.conf import settings

from apps.core.http_client import ServiceClient

_BASE = "/api/v1/componentes-curriculares"

_client = ServiceClient(
    base_url=settings.SIDECAR_PEDAGOGICO_URL,
    dominio="pedagogico",
)


# EP-1 (legado 1,2,3)
def get_componentes_funcionario(
    login,
    id_perfil,
    codigo_turma=None,
    agrupa=False,
    planejamento=False,
    checa_motivo_disponibilizacao=True,
    considera_turma_infantil=True,
):
    params = {"idPerfil": id_perfil}
    if codigo_turma:
        params["codigoTurma"] = codigo_turma
        params["agrupaComponenteCurricular"] = agrupa
        params["planejamento"] = planejamento
        params["checaMotivoDisponibilizacao"] = checa_motivo_disponibilizacao
        params["consideraTurmaInfantil"] = considera_turma_infantil
    return _client.get(f"{_BASE}/funcionarios/{login}", params=params).json()


# EP-2
def get_componentes_regencia(ano_turma):
    return _client.get(f"{_BASE}/anos/{ano_turma}/regencia").json()


# EP-3
def validar_pap(codigo_turma, login, id_perfil):
    params = {"login": login, "idPerfil": id_perfil}
    return _client.get(
        f"{_BASE}/turmas/{codigo_turma}/pap", params=params
    ).json()


# EP-4
def get_componentes_ue_anos(ue_id, modalidade, ano_letivo, anos_escolares):
    params = {"anosEscolares": anos_escolares}
    return _client.get(
        f"{_BASE}/ues/{ue_id}/modalidades/{modalidade}/anos/{ano_letivo}",
        params=params,
    ).json()


# EP-5
def get_componentes_turmas_programa(ue_id, modalidade, ano_letivo):
    return _client.get(
        f"{_BASE}/ues/{ue_id}/modalidades/{modalidade}/anos/{ano_letivo}/turmas-programa"
    ).json()


# EP-6
def get_componentes_por_turmas_ue(ue_id, turmas):
    params = {"turmas": turmas}
    return _client.get(f"{_BASE}/ues/{ue_id}/turmas", params=params).json()


# EP-7
def get_componentes_planejamento(codigo_turmas, adicionar_planejamento=True):
    params = {
        "codigoTurmas": codigo_turmas,
        "adicionarComponentesPlanejamento": adicionar_planejamento,
    }
    return _client.get(f"{_BASE}/turmas", params=params).json()


# EP-8
def get_componentes_brutos(codigo_turmas):
    params = {"codigoTurmas": codigo_turmas}
    return _client.get(f"{_BASE}/turmas/brutos", params=params).json()


# EP-9
def get_catalogo_componentes():
    return _client.get(_BASE).json()


# EP-10
def get_vigencia_componentes(
    ue_codigo, ano_letivo, componentes, semestre=None
):
    params = {
        "ueCodigo": ue_codigo,
        "anoLetivo": ano_letivo,
        "componentesCurriculares": componentes,
    }
    if semestre:
        params["semestre"] = semestre
    return _client.get(f"{_BASE}/turmas/vigencia", params=params).json()


# EP-11
def get_grade_curricular(ano_letivo):
    return _client.get(f"{_BASE}/grade-curricular/{ano_letivo}").json()


# EP-12
def get_sem_atribuicao(codigo_turma, data_base_tick):
    params = {"dataBase": data_base_tick}
    return _client.get(
        f"{_BASE}/turmas/{codigo_turma}/sem-atribuicao", params=params
    ).json()


# EP-13
def get_agrupamentos_correlacionados(codigo, data_base=None):
    params = {}
    if data_base:
        params["dataBase"] = data_base
    return _client.get(
        f"{_BASE}/{codigo}/territorio-saber/agrupamentos-correlacionados",
        params=params or None,
    ).json()


# EP-14
def get_agrupamentos_correlacionados_lote(ids, data_base=None):
    params = {}
    if data_base:
        params["dataBase"] = data_base
    return _client.post(
        f"{_BASE}/territorio-saber/agrupamentos-correlacionados",
        payload=ids,
        params=params or None,
    ).json()


# EP-15
def get_agrupamentos(ids):
    return _client.post(
        f"{_BASE}/territorio-saber/agrupamentos",
        payload=ids,
    ).json()
