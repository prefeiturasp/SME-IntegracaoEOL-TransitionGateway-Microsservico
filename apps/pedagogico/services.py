"""Serviços do domínio pedagógico."""

from datetime import datetime, timedelta
from typing import Any, cast

from django.conf import settings

from apps.alunos import services as alunos_services
from apps.core.datetime import formatar_datetime_legado
from apps.core.http_client import ServiceClient
from apps.professores import services as professores_services

_BASE = "/api/v1/pedagogico/componentes-curriculares"
_BASE_TURMAS = "/api/v1/pedagogico/turmas"

# Elegibilidade das turmas históricas do professor (contrato legado).
_ETAPAS_TURMAS_HISTORICAS = frozenset(
    {1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 17}
)
_TIPOS_ESCOLA_TURMAS_HISTORICAS = frozenset({1, 2, 3, 4, 16, 28, 31})

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


def get_turmas_recorte_por_tipo(
    codigos: list[int],
    tipos_turma: list[int] | None = None,
    ue_codigo: str | None = None,
    semestre: int | None = None,
) -> list[int]:
    """Filtra códigos de turma por tipo de turma, UE e semestre.

    Args:
        codigos: Códigos de turma candidatos (vindos do Alunos-MS).
        tipos_turma: Tipos de turma aceitos; sem filtro quando vazio.
        ue_codigo: Código da UE; sem filtro quando ausente.
        semestre: Semestre da turma; sem filtro quando ausente.

    Returns:
        Subconjunto dos códigos que atende ao recorte.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
    """
    if not codigos:
        return []
    params: dict[str, Any] = {}
    if tipos_turma:
        params["tipos_turma"] = [int(tipo) for tipo in tipos_turma]
    if ue_codigo:
        params["ue_codigo"] = ue_codigo
    if semestre is not None:
        params["semestre"] = semestre
    resp = _client.post(
        f"{_BASE_TURMAS}/recorte-por-tipo/",
        payload=[int(codigo) for codigo in codigos],
        params=params or None,
    )
    resp.raise_for_status()
    dados = _client.json_or_none(resp) or []
    return [int(codigo) for codigo in dados]


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


def get_alunos_ativos_turma_sem_redis(codigo_turma: str) -> Any:
    """Retorna alunos ativos de uma turma sem consulta a cache.

    Args:
        codigo_turma: Código da turma recebida no contrato legado.

    Returns:
        Lista de alunos ativos retornada pelo sidecar pedagógico.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    return alunos_services.get_alunos_por_turma(
        codigo_turma,
        considerar_inativos=False,
        sequencia=1,
    )


def get_alunos_ativos_turma_redis_multplex(codigo_turma: str) -> Any:
    """Retorna alunos ativos de uma turma pelo contrato Redis Multplex.

    Args:
        codigo_turma: Código da turma recebida no contrato legado.

    Returns:
        Lista de alunos ativos retornada pelo sidecar pedagógico.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    return alunos_services.get_alunos_por_turma(
        codigo_turma,
        considerar_inativos=True,
    )


def get_alunos_turma_considera_inativos(
    codigo_turma: str, considera_inativos: bool | None
) -> Any:
    """Retorna alunos na turma considerando ativos ou inativos.

    Args:
        codigo_turma: Código da turma recebida no contrato legado.
        considera_inativos: Considera ativos ou inativos na turma.

    Returns:
        Lista de alunos ativos ou inativos retornada pelo sidecar pedagógico.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    return alunos_services.get_alunos_por_turma(
        codigo_turma,
        considerar_inativos=bool(considera_inativos),
        sequencia=1,
    )


def get_turmas_historicas_gerais_professor(
    ano_letivo: int,
    professor_rf: str,
) -> list[dict[str, Any]]:
    """Lista turmas históricas gerais de um professor.

    Os códigos de turma vêm do domínio professores (cadeia de grade) e os
    atributos de cada turma são obtidos no domínio pedagógico.

    Args:
        ano_letivo: Ano letivo usado na consulta.
        professor_rf: Registro funcional do professor.

    Returns:
        Turmas históricas com os atributos do domínio pedagógico.

    Raises:
        httpx.HTTPStatusError: Se algum sidecar retornar status de erro.
        httpx.RequestError: Se algum sidecar estiver inacessível.
        ValueError: Se alguma resposta não tiver o formato esperado.
    """
    codigos = professores_services.get_codigos_turmas_historicas_professor(
        ano_letivo,
        professor_rf,
    )
    if not codigos:
        return []

    response = _client.post(
        f"{_BASE_TURMAS}/listar-turmas/",
        payload=codigos,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or any(
        not isinstance(item, dict) for item in payload
    ):
        raise ValueError(
            "Resposta de turmas históricas deve ser uma lista de objetos."
        )
    codigos_permitidos = set(codigos)
    turmas: list[dict[str, Any]] = []
    for turma in payload:
        codigo = turma.get("codigo")
        if not isinstance(codigo, int) or isinstance(codigo, bool):
            raise ValueError(
                "Resposta de turmas históricas deve conter código inteiro."
            )
        if codigo in codigos_permitidos and _turma_historica_elegivel(turma):
            turmas.append(turma)
    return turmas


def _turma_historica_elegivel(turma: dict[str, Any]) -> bool:
    """Verifica se a turma atende às etapas e escolas do contrato legado.

    A etapa de ensino é obrigatória; o tipo de escola só restringe quando
    presente no payload.
    """
    if turma.get("codigo_etapa_ensino") not in _ETAPAS_TURMAS_HISTORICAS:
        return False
    tipo_escola = turma.get("tipo_escola")
    if tipo_escola is None:
        return True
    return tipo_escola in _TIPOS_ESCOLA_TURMAS_HISTORICAS


def get_listagem_turmas_componentes(
    codigo_ue: str,
    modalidade: int,
    ano_letivo: int,
    codigo_turma: int | None = None,
    qtde_registros: int | None = None,
    qtde_registros_ignorados: int | None = None,
    eh_professor: bool = False,
    codigo_rf: str | None = None,
    considera_historico: bool = False,
    periodo_escolar_inicio_tick: int | None = None,
    anos_infantil_desconsiderar: list[str] | None = None,
) -> dict[str, Any]:
    """Lista turmas e componentes por UE, modalidade e ano letivo.

    Args:
        codigo_ue: Código da unidade educacional.
        modalidade: Código da modalidade de ensino.
        ano_letivo: Ano letivo consultado.
        codigo_turma: Filtra por uma turma específica quando informado.
        qtde_registros: Tamanho da página usado no total de páginas.
        qtde_registros_ignorados: Compatibilidade legada; repassado ao MS.
        eh_professor: Restringe os componentes ao RF informado.
        codigo_rf: RF do professor usado no filtro e no território.
        considera_historico: Inclui turmas históricas (situação C/E).
        periodo_escolar_inicio_tick: Início do período escolar em ticks .NET.
        anos_infantil_desconsiderar: Anos de turma removidos do retorno.

    Returns:
        Envelope paginado (`items`, `total_registros`, `total_paginas`).

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
        ValueError: Se a resposta não representar um objeto.
        OverflowError: Se os ticks excederem o limite do datetime.
    """
    params: dict[str, Any] = {
        "eh_professor": str(eh_professor).lower(),
        "considera_historico": str(considera_historico).lower(),
    }
    if codigo_turma:
        params["codigo_turma"] = codigo_turma
    if qtde_registros is not None:
        params["qtde_registros"] = qtde_registros
    if qtde_registros_ignorados is not None:
        params["qtde_registros_ignorados"] = qtde_registros_ignorados
    if eh_professor and codigo_rf:
        params["codigo_rf"] = codigo_rf
    if periodo_escolar_inicio_tick:
        params["periodo_escolar_inicio"] = _ticks_dotnet_para_data(
            periodo_escolar_inicio_tick
        )
    if anos_infantil_desconsiderar:
        params["anos_infantil_desconsiderar"] = anos_infantil_desconsiderar

    response = _client.get(
        f"{_BASE}/ues/{codigo_ue}/modalidades/{modalidade}/anos/"
        f"{ano_letivo}/componentes/",
        params=params,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Resposta da listagem de turmas deve ser um objeto.")
    return payload


def get_sincronizacao_institucional_turma(
    codigo_ue: str,
    codigo_turma: str,
) -> dict[str, Any]:
    """Retorna os dados institucionais sincronizados de uma turma.

    Args:
        codigo_ue: Código da unidade educacional.
        codigo_turma: Código da turma.

    Returns:
        Dados institucionais da turma.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
        ValueError: Se a resposta não representar um objeto.
    """
    response = _client.get(
        f"{_BASE_TURMAS}/ues/{codigo_ue}/turmas/{codigo_turma}/"
        "sincronizacoes-institucionais/"
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Resposta institucional da turma deve ser um objeto.")
    return payload


def get_sincronizacoes_institucionais_anos_letivos(
    codigo_ue: str,
    anos_letivos_vigente: list[int] | None = None,
) -> list[int]:
    """Lista turmas institucionais da UE por anos letivos.

    Args:
        codigo_ue: Código da unidade educacional.
        anos_letivos_vigente: Anos letivos usados no filtro.

    Returns:
        Códigos das turmas encontradas.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
        ValueError: Se a resposta não for uma lista de inteiros.
    """
    params = None
    if anos_letivos_vigente:
        params = {"anos_letivos_vigente": anos_letivos_vigente}

    response = _client.get(
        f"{_BASE_TURMAS}/ue/{codigo_ue}/"
        "sincronizacoes-institucionais/anos-letivos/",
        params=params,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or any(
        not isinstance(codigo, int) or isinstance(codigo, bool)
        for codigo in payload
    ):
        raise ValueError(
            "Resposta de anos letivos deve ser uma lista de inteiros."
        )
    return payload


def get_itinerarios_ensino_medio() -> list[dict[str, Any]]:
    """Lista os itinerários do ensino médio.

    Returns:
        Itinerários retornados pelo serviço pedagógico.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
        ValueError: Se a resposta não for uma lista de objetos.
    """
    response = _client.get(f"{_BASE_TURMAS}/itinerario/ensino-medio/")
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or any(
        not isinstance(item, dict) for item in payload
    ):
        raise ValueError(
            "Resposta de itinerários deve ser uma lista de objetos."
        )
    return payload


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


def get_agrupamentos_correlacionados(
    codigo_componente: int,
    data_base_tick: int | None,
) -> Any:
    """Retorna agrupamentos de Território do Saber correlacionados.

    Args:
        codigo_componente: `cod_agrupamento` de origem.
        data_base_tick: Data base em ticks do .NET; None para sem filtro.

    Returns:
        Agrupamentos correlacionados ao `cod_agrupamento` informado.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        OverflowError: Se os ticks excederem o limite do datetime.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    params: dict[str, Any] = {}
    if data_base_tick is not None:
        params["data_base"] = _ticks_dotnet_para_data(data_base_tick)
    return _client.get(
        f"{_BASE}/{codigo_componente}/territorio-saber"
        "/agrupamentos-correlacionados/",
        params=params,
    ).json()


def post_agrupamentos_correlacionados(
    ids: list[int],
    data_base_tick: int | None,
) -> Any:
    """Retorna agrupamentos de Território do Saber correlacionados em lote.

    Args:
        ids: Lista de `cod_agrupamento` de origem.
        data_base_tick: Data base em ticks do .NET; None para sem filtro.

    Returns:
        Agrupamentos correlacionados sem duplicatas.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        OverflowError: Se os ticks excederem o limite do datetime.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    params: dict[str, Any] = {}
    if data_base_tick is not None:
        params["data_base"] = _ticks_dotnet_para_data(data_base_tick)
    return _client.post(
        f"{_BASE}/territorio-saber/agrupamentos-correlacionados/",
        payload=ids,
        params=params,
    ).json()


def post_agrupamentos_territorio(ids: list[int]) -> Any:
    """Retorna agrupamentos de Território do Saber por IDs.

    Args:
        ids: IDs dos agrupamentos a consultar.

    Returns:
        Agrupamentos de Território do Saber encontrados.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
        ValueError: Se a resposta não puder ser convertida para JSON.
    """
    return _client.post(
        f"{_BASE}/territorio-saber/agrupamentos/",
        payload=ids,
    ).json()
