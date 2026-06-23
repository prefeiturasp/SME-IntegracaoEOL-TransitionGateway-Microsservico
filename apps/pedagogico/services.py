"""Serviços do domínio pedagógico."""

from datetime import datetime, timedelta
from typing import Any, cast

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


def listar_turmas(codigos: list[int]) -> Any:
    """Lista dados resumidos de turmas pelos códigos informados.

    Args:
        codigos: Códigos das turmas consultadas.

    Returns:
        Lista de turmas retornada pelo sidecar (inclui ``nome_turma``,
        ``tipo_turno``, ``codigo_etapa_ensino`` e ``codigo_ciclo_ensino``).

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
    """
    resp = _client.post(f"{_BASE_TURMAS}/listar-turmas/", payload=codigos)
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_turmas_recorte_fund_medio_eja(
    codigos: list[int],
) -> list[dict[str, Any]]:
    """Lista turmas no recorte de etapa (Fund/Médio/EJA).

    Args:
        codigos: Códigos das turmas a consultar.

    Returns:
        Turmas no recorte de etapa retornadas pelo sidecar.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
    """
    if not codigos:
        return []
    resp = _client.post(
        f"{_BASE_TURMAS}/recorte-fund-medio-eja/",
        payload=[int(codigo) for codigo in codigos],
    )
    return _client.json_or_none(resp) or []


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


def get_componentes_turma_funcionario(
    codigo_turma: str,
    login: str,
    id_perfil: str,
    agrupa_componente_curricular: bool,
    checa_motivo_disponibilizacao: bool = True,
    considera_turma_infantil: bool = True,
) -> Any:
    """Retorna componentes do funcionário em uma turma.

    Args:
        codigo_turma: Código da turma usada no filtro.
        login: Login/RF do funcionário.
        id_perfil: Identificador do perfil do funcionário.
        agrupa_componente_curricular: Indica se os componentes serão
            agrupados.
        checa_motivo_disponibilizacao: Indica se o motivo de
            disponibilização será considerado.
        considera_turma_infantil: Indica se regras de educação infantil
            serão consideradas.

    Returns:
        Componentes curriculares associados ao funcionário e à turma.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.get(
        f"{_BASE}/funcionarios/{login}",
        params={
            "idPerfil": id_perfil,
            "codigoTurma": codigo_turma,
            "agrupaComponenteCurricular": agrupa_componente_curricular,
            "checaMotivoDisponibilizacao": checa_motivo_disponibilizacao,
            "consideraTurmaInfantil": considera_turma_infantil,
        },
    ).json()


def get_componentes_planejamento(
    codigo_turma: str,
    login: str,
    id_perfil: str,
) -> Any:
    """Retorna componentes de planejamento do funcionário em uma turma.

    Args:
        codigo_turma: Código da turma usada no filtro.
        login: Login/RF do funcionário.
        id_perfil: Identificador do perfil do funcionário.

    Returns:
        Componentes curriculares disponíveis para planejamento.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.get(
        f"{_BASE}/funcionarios/{login}",
        params={
            "idPerfil": id_perfil,
            "codigoTurma": codigo_turma,
            "planejamento": True,
        },
    ).json()


def get_componentes_por_lista_turmas(
    codigos_turmas: list[str],
    adicionar_componentes_planejamento: bool = True,
) -> Any:
    """Retorna componentes para planejamento por lista de turmas.

    Args:
        codigos_turmas: Códigos das turmas usadas no filtro.
        adicionar_componentes_planejamento: Indica se componentes de
            planejamento serão adicionados.

    Returns:
        Componentes curriculares das turmas informadas.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.get(
        f"{_BASE}/turmas",
        params={
            "codigoTurmas": codigos_turmas,
            "adicionarComponentesPlanejamento": (
                adicionar_componentes_planejamento
            ),
        },
    ).json()


def get_componentes_turmas_regulares(codigos_turmas: list[str]) -> Any:
    """Retorna componentes de turmas regulares.

    Args:
        codigos_turmas: Códigos das turmas usadas no filtro.

    Returns:
        Componentes curriculares das turmas regulares informadas.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.get(
        f"{_BASE}/turmas/brutos",
        params={"codigoTurmas": codigos_turmas},
    ).json()


def get_dados_aula_turma(
    ue_codigo: str,
    ano_letivo: int,
    componentes_curriculares: list[str],
    semestre: int | None = None,
) -> list[dict[str, Any]]:
    """Retorna dados de aula por turma e componente.

    Args:
        ue_codigo: Código da unidade educacional.
        ano_letivo: Ano letivo usado no filtro.
        componentes_curriculares: Códigos dos componentes curriculares.
        semestre: Semestre usado no filtro, quando informado.

    Returns:
        Dados de vigência dos componentes no formato legado.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    params: dict[str, Any] = {
        "ueCodigo": ue_codigo,
        "anoLetivo": ano_letivo,
        "componentesCurriculares": componentes_curriculares,
    }
    if semestre is not None:
        params["semestre"] = semestre

    payload = _client.get(
        f"{_BASE}/turmas/vigencia",
        params=params,
    ).json()
    return [
        {
            "componenteCurricularCodigo": item["componente_codigo"],
            "componenteCurricularDescricao": item["componente_descricao"],
            "turmaCodigo": item["turma_codigo"],
            "dataInicioTurma": formatar_datetime_legado(
                item.get("data_inicio_turma")
            ),
        }
        for item in payload
    ]


def _ticks_dotnet_para_data(data_base_tick: int) -> str:
    """Converta ticks de DateTime do .NET para data ISO.

    Args:
        data_base_tick: Quantidade de intervalos de 100 nanossegundos desde
            0001-01-01.

    Returns:
        Data no formato ISO 8601.

    Raises:
        OverflowError: Se os ticks excederem o limite do datetime.
    """
    data_base = datetime(1, 1, 1) + timedelta(
        microseconds=data_base_tick // 10
    )
    return data_base.date().isoformat()


def get_componentes_sem_atribuicao(
    codigo_turma: str,
    data_base_tick: int,
) -> list[str]:
    """Retorna componentes sem atribuição na data informada.

    Args:
        codigo_turma: Código da turma usada no filtro.
        data_base_tick: Data base representada em ticks do .NET.

    Returns:
        Descrições dos componentes sem professor atribuído.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        OverflowError: Se os ticks excederem o limite do datetime.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return cast(
        list[str],
        _client.get(
            f"{_BASE}/turmas/{codigo_turma}/sem-atribuicao",
            params={"data_base": _ticks_dotnet_para_data(data_base_tick)},
        ).json(),
    )


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
