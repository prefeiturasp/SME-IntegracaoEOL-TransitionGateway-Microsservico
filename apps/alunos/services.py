"""Serviços do domínio de alunos."""

from datetime import datetime
from typing import Any

from django.conf import settings

from apps.core.http_client import ServiceClient

_BASE = "/api/v1/alunos"
_BASE_UES = f"{_BASE}/ues"

_client = ServiceClient(
    base_url=settings.SIDECAR_ALUNOS_URL,
    dominio="alunos",
    api_key=settings.SIDECAR_ALUNOS_API_KEY,
    api_key_header=settings.SIDECAR_ALUNOS_API_KEY_HEADER,
)


def get_informacoes_aluno(codigo_aluno: str) -> Any:
    """Retorna informações do aluno, ou ``None`` se não encontrado.

    Args:
        codigo_aluno: Código EOL do aluno.

    Returns:
        Payload retornado pelo sidecar, ou ``None`` quando não houver corpo.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/{codigo_aluno}/informacoes")
    resp.raise_for_status()
    return _client.json_or_none(resp)


def get_necessidades_especiais_aluno(codigo_aluno: str) -> Any:
    """Retorna a necessidade especial principal do aluno.

    Args:
        codigo_aluno: Código EOL do aluno.

    Returns:
        Lista de necessidades especiais retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/{codigo_aluno}/necessidades-especiais")
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def buscar_alunos_ativos_autocomplete(
    ue_codigo: str,
    aluno_nome: str | None,
    data_referencia: datetime | None,
    aluno_codigo: int,
    limite: int,
) -> Any:
    """Busca alunos ativos para autocomplete por UE e filtros.

    Args:
        ue_codigo: Código da unidade educacional.
        aluno_nome: Nome parcial do aluno para filtro.
        data_referencia: Data usada como referência de situação ativa.
        aluno_codigo: Código EOL do aluno para filtro direto.
        limite: Quantidade máxima de resultados.

    Returns:
        Lista de alunos encontrados ou lista vazia.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, Any] = {
        "aluno_codigo": aluno_codigo,
        "limite": limite,
    }
    if aluno_nome:
        params["aluno_nome"] = aluno_nome
    if data_referencia:
        params["data_referencia"] = data_referencia.isoformat()
    resp = _client.get(
        f"{_BASE_UES}/{ue_codigo}/autocomplete/ativos",
        params=params,
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_alunos_autocomplete_ue(
    codigo_ue: str,
    ano_letivo: str,
    codigo_turmas: list[str] | None = None,
    nome_aluno: str | None = None,
    codigo_eol: str | None = None,
    somente_ativos: str | None = None,
    eh_historico: str | None = None,
    limite: int = 10,
) -> Any:
    """Busca alunos da UE/ano para autocomplete.

    Args:
        codigo_ue: Código da unidade educacional.
        ano_letivo: Ano letivo consultado.
        codigo_turmas: Códigos de turma usados como filtro opcional.
        nome_aluno: Nome parcial do aluno para filtro.
        codigo_eol: Código EOL do aluno para filtro direto.
        somente_ativos: Indicador repassado por compatibilidade.
        eh_historico: Consulta os vínculos históricos quando verdadeiro.
        limite: Quantidade máxima de resultados.

    Returns:
        Lista de alunos encontrados ou lista vazia.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, Any] = {"limite": limite}
    if codigo_turmas:
        params["codigos_turmas"] = codigo_turmas
    if nome_aluno:
        params["nome_aluno"] = nome_aluno
    if codigo_eol:
        params["codigo_eol"] = codigo_eol
    if somente_ativos is not None:
        params["somente_ativos"] = somente_ativos
    if eh_historico is not None:
        params["eh_historico"] = eh_historico
    resp = _client.get(
        f"{_BASE_UES}/{codigo_ue}/anos_letivos/{ano_letivo}/autocomplete",
        params=params,
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_dados_acompanhamento_escolar(
    codigo_aluno: str | None = None,
    codigo_dre: str | None = None,
    codigo_ue: str | None = None,
    cpf_responsavel: str | None = None,
) -> Any:
    """Busca dados de acompanhamento escolar dos alunos.

    Args:
        codigo_aluno: Código EOL do aluno usado como filtro opcional.
        codigo_dre: Código da DRE usado como filtro opcional.
        codigo_ue: Código da UE usado como filtro opcional.
        cpf_responsavel: CPF do responsável usado como filtro opcional.

    Returns:
        Lista de dados de acompanhamento ou lista vazia.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, Any] = {}
    if codigo_aluno:
        params["codigo_aluno"] = codigo_aluno
    if codigo_dre:
        params["codigo_dre"] = codigo_dre
    if codigo_ue:
        params["codigo_ue"] = codigo_ue
    if cpf_responsavel:
        params["cpf_responsavel"] = cpf_responsavel
    resp = _client.get(
        f"{_BASE}/dados-acompanhamento-escolar/contrato",
        params=params or None,
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_turmas_aluno_com_historico(
    codigo_aluno: str,
    ano_letivo: str,
    historico: str,
    filtrar_situacao: str,
    tipo_turma: str,
) -> Any:
    """Retorna turmas do aluno com a origem histórica explícita.

    Args:
        codigo_aluno: Código EOL do aluno.
        ano_letivo: Ano letivo consultado.
        historico: Consulta os vínculos históricos quando verdadeiro.
        filtrar_situacao: Restringe às situações de matrícula válidas.
        tipo_turma: Exclui turmas do tipo programa quando verdadeiro.

    Returns:
        Lista de turmas retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_aluno}/turmas/anos_letivos/{ano_letivo}"
        f"/historico/{historico}/filtrar_situacao/{filtrar_situacao}"
        f"/tipo_turma/{tipo_turma}"
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def listar_alunos_por_ano(
    ano_letivo: str,
    codigos_aluno: list[str],
) -> Any:
    """Retorna alunos pelos códigos informados restritos ao ano letivo.

    Args:
        ano_letivo: Ano letivo consultado.
        codigos_aluno: Códigos EOL dos alunos.

    Returns:
        Lista de alunos retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, Any] = {"codigos_aluno": codigos_aluno}
    resp = _client.get(
        f"{_BASE}/ano_letivo/{ano_letivo}/alunos", params=params
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_quantidade_matriculados_cc(
    ano_letivo: str,
    componentes_curriculares: list[str],
    dre_id: str | None = None,
    ue_id: str | None = None,
) -> Any:
    """Busca matriculados por componente curricular no ano letivo.

    Args:
        ano_letivo: Ano letivo consultado.
        componentes_curriculares: Códigos dos componentes curriculares.
        dre_id: Código da DRE usado como filtro opcional.
        ue_id: Código da UE usado como filtro opcional.

    Returns:
        Lista de quantidades agregadas ou lista vazia.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, Any] = {
        "componentes_curriculares": componentes_curriculares
    }
    if dre_id:
        params["dre_id"] = dre_id
    if ue_id:
        params["ue_id"] = ue_id
    resp = _client.get(
        f"{_BASE}/ano-letivo/{ano_letivo}/matriculados/contrato",
        params=params,
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_quantidade_matriculados(
    ano_letivo: str,
    dre_codigo: str | None = None,
    ue_codigo: str | None = None,
    modalidade: list[str] | None = None,
    ano: list[str] | None = None,
    turma: list[str] | None = None,
) -> Any:
    """Busca a quantidade de alunos matriculados por ano letivo.

    Args:
        ano_letivo: Ano letivo consultado.
        dre_codigo: Código da DRE usado como filtro opcional.
        ue_codigo: Código da UE usado como filtro opcional.
        modalidade: Códigos de modalidade usados como filtro.
        ano: Séries usadas como filtro.
        turma: Códigos de turma usados como filtro.

    Returns:
        Lista de quantidades agregadas ou lista vazia.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, Any] = {}
    if dre_codigo:
        params["dre_codigo"] = dre_codigo
    if ue_codigo:
        params["ue_codigo"] = ue_codigo
    if modalidade:
        params["modalidade"] = modalidade
    if ano:
        params["ano"] = ano
    if turma:
        params["turma"] = turma
    resp = _client.get(
        f"{_BASE}/ano-letivo/{ano_letivo}/matriculados/quantidade/contrato",
        params=params or None,
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_responsavel_resumido(cpf_responsavel: str) -> Any:
    """Retorna dados resumidos de um responsável.

    Args:
        cpf_responsavel: CPF do responsável.

    Returns:
        Payload retornado pelo sidecar, ou ``None`` quando não houver corpo.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/responsaveis/{cpf_responsavel}/resumido")
    resp.raise_for_status()
    return _client.json_or_none(resp)


def get_responsaveis(
    codigo_dre: str | None = None,
    codigo_ue: str | None = None,
    ano_letivo: int | None = None,
) -> Any:
    """Retorna responsáveis aptos ao acompanhamento por turma.

    Args:
        codigo_dre: Código EOL da DRE usado como filtro opcional.
        codigo_ue: Código EOL da UE usado como filtro opcional.
        ano_letivo: Ano letivo usado como filtro opcional.

    Returns:
        Lista de responsáveis retornada pelo serviço de Alunos.

    Raises:
        httpx.HTTPStatusError: Se o serviço retornar status de erro.
        httpx.RequestError: Se o serviço estiver inacessível.
    """
    params: dict[str, Any] = {}
    if codigo_dre:
        params["codigo_dre"] = codigo_dre
    if codigo_ue:
        params["codigo_ue"] = codigo_ue
    if ano_letivo is not None:
        params["ano_letivo"] = ano_letivo
    resp = _client.get(f"{_BASE}/responsaveis", params=params or None)
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_filiacao_aluno(codigo_aluno: str) -> Any:
    """Retorna os dados de filiação do aluno.

    Args:
        codigo_aluno: Código EOL do aluno.

    Returns:
        Lista de responsáveis retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/{codigo_aluno}/responsaveis/filiacao")
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_informacoes_alunos_turma(codigo_turma: str) -> Any:
    """Retorna informações resumidas dos alunos de uma turma.

    Args:
        codigo_turma: Código EOL da turma.

    Returns:
        Lista de alunos da turma, ou lista vazia quando não houver registros.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/{codigo_turma}/turma/informacoes")
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_alunos_por_turma(
    codigo_turma: str,
    *,
    considerar_inativos: bool,
    codigo_aluno: str | None = None,
    data_aula_ticks: str | int | None = None,
    data_matricula_ticks: str | int | None = None,
    sequencia: int | None = None,
) -> Any:
    """Retorna os alunos de uma turma consultando o endpoint canônico.

    Args:
        codigo_turma: Código EOL da turma.
        considerar_inativos: Inclui alunos inativos quando ``True``.
        codigo_aluno: Codigo EOL do aluno usado no filtro.
        data_aula_ticks: Data de referência em ticks de DateTime do .NET.
            Omitido quando ``None`` ou ``0``.
        sequencia: Sequência da matrícula a filtrar, quando aplicável.

    Returns:
        Lista de alunos, ou lista vazia quando não houver registros.

    Raises:
        httpx.HTTPStatusError: Se o serviço externo retornar status de erro.
        httpx.RequestError: Se o serviço externo estiver inacessível.
    """
    params: dict[str, Any] = {"considerar_inativos": considerar_inativos}
    if codigo_aluno is not None:
        params["codigo_aluno"] = codigo_aluno
    if data_aula_ticks is not None and int(data_aula_ticks) != 0:
        params["data_aula_ticks"] = data_aula_ticks
    if data_matricula_ticks is not None:
        params["data_matricula_ticks"] = data_matricula_ticks
    if sequencia is not None:
        params["sequencia"] = sequencia

    resp = _client.get(f"{_BASE}/turmas/{codigo_turma}/", params=params)
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_alunos_ativos_data_aula_ticks(
    codigo_turma: str,
    data_ticks: str,
) -> Any:
    """Retorna alunos ativos da turma na data informada em ticks.

    Args:
        codigo_turma: Código EOL da turma.
        data_ticks: Data de referência em ticks de DateTime do .NET.

    Returns:
        Lista de alunos ativos, ou lista vazia quando não houver registros.

    Raises:
        httpx.HTTPStatusError: Se o serviço externo retornar status de erro.
        httpx.RequestError: Se o serviço externo estiver inacessível.
    """
    return get_alunos_por_turma(
        codigo_turma, considerar_inativos=True, data_aula_ticks=data_ticks
    )


def get_alunos_data_matricula_ticks(
    codigo_turma: str,
    data_matricula_ticks: str,
) -> Any:
    """Retorna alunos da turma por data de matricula."""
    return get_alunos_por_turma(
        codigo_turma,
        considerar_inativos=True,
        data_matricula_ticks=data_matricula_ticks,
        sequencia=1,
    )


def get_turmas_aluno(codigo_aluno: str) -> Any:
    """Retorna turmas do aluno.

    Args:
        codigo_aluno: Código do aluno.

    Returns:
        Lista de turmas retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/{codigo_aluno}/turmas/")
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_alunos_da_ue(
    codigo_ue: str,
    ano_letivo: str,
    nome_aluno: str | None = None,
    codigo_eol: str | None = None,
) -> Any:
    """Retorna alunos matriculados em uma UE no ano letivo informado.

    Args:
        codigo_ue: Código EOL da unidade educacional.
        ano_letivo: Ano letivo consultado.
        nome_aluno: Nome parcial usado para filtrar alunos.
        codigo_eol: Código EOL usado para filtrar um aluno.

    Returns:
        Lista de alunos retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, str] = {}
    if nome_aluno:
        params["nome_aluno"] = nome_aluno
    if codigo_eol:
        params["codigo_eol"] = codigo_eol
    resp = _client.get(
        f"{_BASE_UES}/{codigo_ue}/anos_letivos/{ano_letivo}",
        params=params or None,
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_turmas_aluno_com_programa(codigo_aluno: str) -> Any:
    """Retorna turmas do aluno no ano corrente, incluindo turmas de programa.

    Chama o endpoint de turmas com os filtros desativados
    para tipo_turma e filtragem da situação.

    Args:
        codigo_aluno: Código do aluno.

    Returns:
        Lista de turmas (regulares e de programa) retornada pelo sidecar.
        Lista vazia quando o sidecar responde 4xx (código inválido como
        ``"00000"`` ou aluno sem turmas).

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar erro de servidor (5xx).
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_aluno}/turmas/",
        params={"tipo_turma": "false", "filtrar_situacao": "false"},
    )
    if resp.status_code in (400, 404):
        return []
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_turmas_aluno_por_situacao(
    codigo_aluno: str,
    ano_letivo: str,
    filtrar_situacao_matricula: str,
    tipo_turma: str,
) -> Any:
    """Retorna turmas do aluno filtradas por situação de matrícula e tipo.

    Args:
        codigo_aluno: Código EOL do aluno.
        ano_letivo: Ano letivo consultado.
        filtrar_situacao_matricula: Indicador booleano (``true``/``false``).
        tipo_turma: Indicador booleano (``true``/``false``).

    Returns:
        Lista de turmas retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_aluno}/turmas/anos_letivos/{ano_letivo}"
        f"/matricula_turma/{filtrar_situacao_matricula}"
        f"/tipo_turma/{tipo_turma}"
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_alunos_ativos_turma(codigo_turma: str) -> Any:
    """Retorna os alunos ativos de uma turma.

    Args:
        codigo_turma: Código EOL da turma.

    Returns:
        Lista de alunos ativos retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    resp = _client.get(f"{_BASE}/turmas/{codigo_turma}/ativos")
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_alunos_ativos_turma_periodo(
    codigo_turma: str,
    data_referencia_fim: str,
    data_referencia_inicio: str | None = None,
) -> Any:
    """Retorna alunos ativos de uma turma no período informado.

    Args:
        codigo_turma: Código EOL da turma.
        data_referencia_fim: Data final usada na consulta.
        data_referencia_inicio: Data inicial opcional da consulta.

    Returns:
        Lista de alunos ativos retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params = (
        {"data_referencia_inicio": data_referencia_inicio}
        if data_referencia_inicio
        else None
    )
    resp = _client.get(
        f"{_BASE}/turmas/{codigo_turma}/ativos/{data_referencia_fim}",
        params=params,
    )
    resp.raise_for_status()
    return _client.json_or_none(resp) or []


def get_total_alunos_ativos_periodo(
    ano_turma: str,
    ano_letivo: str,
    data_inicio: str,
    data_fim: str,
    ue_id: str | None = None,
    dre_id: str | None = None,
    modalidades: list[str] | None = None,
) -> Any:
    """Retorna o total de alunos ativos no período.

    Args:
        ano_turma: Ano escolar usado no filtro.
        ano_letivo: Ano letivo consultado.
        data_inicio: Data inicial do período.
        data_fim: Data final do período.
        ue_id: Código opcional da unidade educacional.
        dre_id: Código opcional da diretoria regional de educação.
        modalidades: Códigos opcionais das modalidades de ensino.

    Returns:
        Total retornado pelo serviço de alunos.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, Any] = {}
    if ue_id:
        params["ue_id"] = ue_id
    if dre_id:
        params["dre_id"] = dre_id
    if modalidades:
        params["modalidades"] = modalidades
    resp = _client.get(
        f"{_BASE}/ativos/anos/{ano_turma}/anos-letivos/{ano_letivo}"
        f"/inicio/{data_inicio}/fim/{data_fim}",
        params=params or None,
    )
    resp.raise_for_status()
    return _client.json_or_none(resp)


def get_codigos_turmas_regulares_aluno(
    ano_letivo: str,
    codigo_aluno: str,
    data_referencia: str | None = None,
) -> list[int]:
    """Lista os códigos de turma do aluno no ano letivo (recorte de matrícula).

    Args:
        ano_letivo: Ano letivo consultado.
        codigo_aluno: Código EOL do aluno.
        data_referencia: Data de referência (ISO) do filtro de situação.

    Returns:
        Códigos de turma ordenados por data da situação decrescente. Lista
        vazia quando o sidecar responde 4xx (código inválido ou sem
        vínculos).

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar erro de servidor (5xx).
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, Any] = {}
    if data_referencia:
        params["data_referencia"] = data_referencia
    resp = _client.get(
        f"{_BASE}/anos-letivos/{ano_letivo}/alunos/{codigo_aluno}"
        "/codigos-turmas-regulares",
        params=params or None,
    )
    if resp.status_code in (400, 404):
        return []
    resp.raise_for_status()
    dados = _client.json_or_none(resp) or []
    return [int(codigo) for codigo in dados]


def montar_codigos_turmas_regulares_aluno(
    ano_letivo: str,
    codigo_aluno: str,
    tipos_turma: list[int] | None = None,
    ue_codigo: str | None = None,
    data_referencia: str | None = None,
    semestre: int | None = None,
) -> list[int]:
    """Compõe os códigos de turma regulares do aluno.

    Args:
        ano_letivo: Ano letivo consultado.
        codigo_aluno: Código EOL do aluno.
        tipos_turma: Tipos de turma aceitos; sem filtro quando vazio.
        ue_codigo: Código da UE; sem filtro quando ausente.
        data_referencia: Data de referência (ISO) do filtro de situação.
        semestre: Semestre da turma; sem filtro quando ausente.

    Returns:
        Códigos de turma que atendem ao recorte, na ordem do Alunos-MS.

    Raises:
        httpx.HTTPStatusError: Se algum sidecar retornar erro de servidor.
        httpx.RequestError: Se algum sidecar estiver inacessível.
    """
    from apps.pedagogico import services as pedagogico_services

    codigos = get_codigos_turmas_regulares_aluno(
        ano_letivo, codigo_aluno, data_referencia
    )
    if not codigos:
        return []
    permitidos = set(
        pedagogico_services.get_turmas_recorte_por_tipo(
            codigos, tipos_turma, ue_codigo, semestre
        )
    )
    return [codigo for codigo in codigos if codigo in permitidos]


def listar_alunos(codigos_aluno: list[str]) -> Any:
    """Retorna lista de alunos pelos códigos informados.

    Args:
        codigos_aluno: Códigos dos alunos usados no filtro.

    Returns:
        Lista de alunos retornada pelo sidecar.

    Raises:
        httpx.HTTPStatusError: Se o sidecar retornar status de erro.
        httpx.RequestError: Se o sidecar estiver inacessível.
    """
    params: dict[str, Any] = {"codigos_aluno": codigos_aluno}
    resp = _client.get(f"{_BASE}/alunos", params=params)
    resp.raise_for_status()
    return _client.json_or_none(resp) or []
