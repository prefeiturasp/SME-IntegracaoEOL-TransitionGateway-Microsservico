"""Serviços de integração do domínio professores."""

from typing import Any

from django.conf import settings

from apps.core.datetime import datetime_legado
from apps.core.http_client import ServiceClient
from apps.institucional import services as institucional_services
from apps.pedagogico import services as pedagogico_services

_BASE = "/api/v1/professores"
_BASE_ACESSOS = f"{_BASE}/acessos"
_BASE_FUNCIONARIOS = f"{_BASE}/funcionarios"
_BASE_ESCOLAS = f"{_BASE}/escolas"

_client = ServiceClient(
    base_url=settings.SIDECAR_PROFESSORES_URL,
    dominio="professores",
    api_key=settings.SIDECAR_PROFESSORES_API_KEY,
    api_key_header=settings.SIDECAR_PROFESSORES_API_KEY_HEADER,
)


def _valores_param(
    params: dict[str, str | list[str]],
    nome: str,
) -> list[str]:
    """Retorna valores não vazios de um parâmetro de filtro.

    Args:
        params: Parâmetros recebidos para a consulta.
        nome: Nome do parâmetro consultado.

    Returns:
        Lista normalizada de valores informados.
    """
    value = params.get(nome)
    if isinstance(value, list):
        return [item for item in value if item]
    if value:
        return [value]
    return []


def _params_com_valor(
    params: dict[str, str | list[str]],
    nome: str,
    nome_destino: str,
    value: str,
) -> dict[str, str | list[str]]:
    """Retorna parâmetros com um único valor de filtro.

    Args:
        params: Parâmetros recebidos para a consulta.
        nome: Nome original do parâmetro de filtro.
        nome_destino: Nome usado no parâmetro de saída.
        value: Valor isolado para a consulta.

    Returns:
        Cópia dos parâmetros com o filtro normalizado.
    """
    params_filtrados = params.copy()
    if nome_destino != nome:
        params_filtrados.pop(nome, None)
    params_filtrados[nome_destino] = [value]
    return params_filtrados


def _adicionar_id_filtro(
    data: Any,
    value: str | None,
    nome_campo: str,
) -> Any:
    """Adiciona o identificador do filtro quando a lista não o contém.

    Args:
        data: Dados retornados pela consulta.
        value: Valor do filtro usado na consulta.
        nome_campo: Campo que receberá o identificador.

    Returns:
        Dados com o identificador preenchido quando aplicável.

    Raises:
        ValueError: Quando o valor do filtro não for numérico.
    """
    if not value or not isinstance(data, list):
        return data
    return [
        (
            {**item, nome_campo: int(value)}
            if isinstance(item, dict) and nome_campo not in item
            else item
        )
        for item in data
    ]


def _get_funcionarios_escola_por_filtro(
    codigo_ue: str,
    params: dict[str, str | list[str]],
    nome_param: str,
    nome_campo: str,
    nome_param_sidecar: str | None = None,
) -> Any:
    """Lista funcionários de escola para cada valor de filtro.

    Args:
        codigo_ue: Código da unidade escolar usada na consulta.
        params: Parâmetros recebidos para a consulta.
        nome_param: Nome do filtro recebido.
        nome_campo: Campo preenchido com o valor do filtro.
        nome_param_sidecar: Nome alternativo usado na consulta.

    Returns:
        Lista consolidada de funcionários encontrados.

    Raises:
        ValueError: Quando algum valor do filtro não for numérico.
    """
    path = f"{_BASE_ESCOLAS}/{codigo_ue}/funcionarios/"
    valores = _valores_param(params, nome_param)
    if not valores:
        return []

    nome_destino = nome_param_sidecar or nome_param
    resultado: list[Any] = []
    for value in valores:
        resp = _client.get(
            path,
            params=_params_com_valor(params, nome_param, nome_destino, value),
        )
        data = _client.json_or_none(resp)
        data = _adicionar_id_filtro(data, value, nome_campo)
        if isinstance(data, list):
            resultado.extend(data)
    return resultado


def get_professor(rf_professor: str) -> Any:
    """Retorna o nome do professor.

    Args:
        rf_professor: Registro funcional usado na consulta.

    Returns:
        Nome obtido na consulta, texto bruto ou ausência de conteúdo.
    """
    resp = _client.get(f"{_BASE}/{rf_professor}")
    data = _client.json_or_none(resp)
    if isinstance(data, dict):
        return data.get("nome")
    return data


def get_validade_professor(codigo_rf: str) -> Any:
    """Verifica se o professor está válido para uso.

    Args:
        codigo_rf: RF usado na consulta de validade.

    Returns:
        Indicador de validade obtido na consulta.
    """
    resp = _client.get(f"{_BASE}/{codigo_rf}/validade")
    return resp.json()


def get_funcionario_ativo(registro_funcional: str) -> Any:
    """Verifica se o funcionário está ativo.

    Args:
        registro_funcional: Registro funcional usado na consulta.

    Returns:
        Indicador de situação ativa obtido na consulta.
    """
    resp = _client.get(
        f"{_BASE_ACESSOS}/funcionario-ativo/{registro_funcional}"
    )
    return resp.json()


def get_nome_servidor(registro_funcional: str) -> Any:
    """Retorna dados de identificação do servidor.

    Args:
        registro_funcional: Registro funcional usado na consulta.

    Returns:
        Dados de identificação do servidor ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS}/nome-servidor/{registro_funcional}"
    )
    return _client.json_or_none(resp)


def get_nome_usuario_eol(registro_funcional: str) -> Any:
    """Retorna nome de usuário EOL do funcionário.

    Args:
        registro_funcional: Registro funcional usado na consulta.

    Returns:
        Nome de usuário EOL ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS}/nome-usuario-eol/{registro_funcional}"
    )
    return _client.json_or_none(resp)


def get_professor_por_rf(
    codigo_rf: str,
    ano_letivo: int,
    buscar_outros_cargos: bool | None = None,
) -> Any:
    """Retorna professor por RF e ano letivo.

    Args:
        codigo_rf: RF usado na consulta.
        ano_letivo: Ano letivo de referência.
        buscar_outros_cargos: Indica se a consulta inclui outros cargos.

    Returns:
        Dados do professor ou ausência de conteúdo.
    """
    path = f"{_BASE}/{codigo_rf}/BuscarPorRf/{ano_letivo}"
    params = None
    if buscar_outros_cargos is not None:
        params = {"buscar_outros_cargos": buscar_outros_cargos}
    if params is None:
        resp = _client.get(path)
    else:
        resp = _client.get(path, params=params)
    return _client.json_or_none(resp)


def get_professores_por_lista_rf(codigos_rf: list[str]) -> Any:
    """Retorna professores pelos RFs informados.

    Args:
        codigos_rf: RFs usados na consulta.

    Returns:
        Lista de professores ou ausência de conteúdo.
    """
    resp = _client.post(
        f"{_BASE_FUNCIONARIOS}/BuscarPorListaRF/",
        payload=codigos_rf,
    )
    return _client.json_or_none(resp)


def get_funcionarios_escola(codigo_ue: str) -> Any:
    """Retorna funcionários vinculados à escola.

    Args:
        codigo_ue: Código da unidade escolar usada na consulta.

    Returns:
        Lista de funcionários da escola ou ausência de conteúdo.
    """
    resp = _client.get(f"{_BASE_ESCOLAS}/{codigo_ue}/funcionarios/")
    return _client.json_or_none(resp)


def get_funcionarios_escola_por_cargo(
    codigo_ue: str,
    codigo_cargo: str,
) -> Any:
    """Retorna funcionários da escola filtrados por cargo.

    Args:
        codigo_ue: Código da unidade escolar usada na consulta.
        codigo_cargo: Código do cargo usado como filtro.

    Returns:
        Lista de funcionários filtrados por cargo ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE_ESCOLAS}/{codigo_ue}/funcionarios/?cargos={codigo_cargo}"
    )
    return _client.json_or_none(resp)


def get_funcionarios_escola_cargos(
    codigo_ue: str,
    params: dict[str, str | list[str]],
) -> Any:
    """Retorna funcionários da escola filtrados por cargos.

    Args:
        codigo_ue: Código da unidade escolar usada na consulta.
        params: Parâmetros de filtro recebidos para a consulta.

    Returns:
        Lista de funcionários filtrados por cargos ou ausência de conteúdo.

    Raises:
        ValueError: Quando algum código de cargo não for numérico.
    """
    return _get_funcionarios_escola_por_filtro(
        codigo_ue,
        params,
        "cargos",
        "cargo_id",
    )


def get_funcionarios_escola_funcoes_atividades(
    codigo_ue: str,
    params: dict[str, str | list[str]],
) -> Any:
    """Retorna funcionários da escola por funções atividades.

    Args:
        codigo_ue: Código da unidade escolar usada na consulta.
        params: Parâmetros de filtro recebidos para a consulta.

    Returns:
        Lista de funcionários por funções atividades ou ausência de conteúdo.

    Raises:
        ValueError: Quando alguma função atividade não for numérica.
    """
    return _get_funcionarios_escola_por_filtro(
        codigo_ue,
        params,
        "funcoes_atividades",
        "codigo_funcao_atividade",
    )


def get_funcionarios_escola_funcoes_externas(
    codigo_ue: str,
    params: dict[str, str | list[str]],
) -> Any:
    """Retorna funcionários da escola por funções externas.

    Args:
        codigo_ue: Código da unidade escolar usada na consulta.
        params: Parâmetros de filtro recebidos para a consulta.

    Returns:
        Lista de funcionários por funções externas ou ausência de conteúdo.

    Raises:
        ValueError: Quando alguma função externa não for numérica.
    """
    return _get_funcionarios_escola_por_filtro(
        codigo_ue,
        params,
        "funcoes",
        "funcao_externo",
        "funcoes_externas",
    )


def get_funcionarios_escola_por_funcao_externa(
    codigo_ue: str,
    codigo_funcao_externa: str,
) -> Any:
    """Retorna funcionários da escola por uma função externa específica.

    Args:
        codigo_ue: Código da unidade escolar usada na consulta.
        codigo_funcao_externa: Código da função externa usado como filtro.

    Returns:
        Lista de funcionários da função externa ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE_ESCOLAS}/{codigo_ue}/funcionarios/",
        params={"funcoes_externas": codigo_funcao_externa},
    )
    return _client.json_or_none(resp)


def get_funcionarios_escola_por_funcao_atividade(
    codigo_ue: str,
    codigo_funcao_atividade: str,
) -> Any:
    """Retorna funcionários da escola por uma função atividade específica.

    Args:
        codigo_ue: Código da unidade escolar usada na consulta.
        codigo_funcao_atividade: Código da função atividade usado como filtro.

    Returns:
        Lista de funcionários da função atividade ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE_ESCOLAS}/{codigo_ue}/funcionarios/",
        params={"funcoes_atividades": codigo_funcao_atividade},
    )
    return _client.json_or_none(resp)


def get_turmas_professor(codigo_rf: str) -> Any:
    """Retorna turmas atribuídas ao professor.

    Args:
        codigo_rf: RF usado na consulta.

    Returns:
        Lista de turmas atribuídas ou ausência de conteúdo.
    """
    resp = _client.get(f"{_BASE}/{codigo_rf}/turmas/")
    return _client.json_or_none(resp)


def _montar_turma_atribuida(
    ancora: dict[str, Any],
    turma: dict[str, Any],
    ue: dict[str, Any],
) -> dict[str, Any]:
    """Monta uma linha de turma atribuída a partir dos três domínios.

    Args:
        ancora: Atribuição vigente do professor.
        turma: Dados da turma no recorte de etapa.
        ue: Dados da UE no recorte de tipo.

    Returns:
        Dicionário em snake_case pronto para serialização.
    """
    return {
        "cod_escola": ue.get("codigo"),
        "cod_turma": ancora.get("codigo_turma"),
        "tipo_turma": turma.get("tipo_turma"),
        "ano": turma.get("ano"),
        "ano_letivo": turma.get("ano_letivo"),
        "cod_modalidade": turma.get("codigo_modalidade"),
        "cod_dre": ue.get("codigoDRE"),
        "dre": ue.get("nomeDRE"),
        "dre_abrev": ue.get("siglaDRE"),
        "modalidade": turma.get("modalidade"),
        "nome_turma": turma.get("nome_turma"),
        "semestre": turma.get("semestre"),
        "tipo_ue": ue.get("tipoUnidade"),
        "cod_tipo_ue": ue.get("codigoTipoUnidadeEducacao"),
        "cod_ue": ue.get("codigo"),
        "ue": ue.get("nome"),
        "ue_abrev": ue.get("nomeExibicao"),
        "tipo_escola": ue.get("siglaTipoEscola"),
        "cod_tipo_escola": ue.get("codigoTipoEscola"),
        "duracao_turno": turma.get("duracao_turno"),
        "tipo_turno": turma.get("tipo_turno"),
        "ensino_especial": turma.get("ensino_especial"),
        "serie_ensino": turma.get("serie_ensino"),
        "data_inicio_turma": datetime_legado(turma.get("data_inicio_turma")),
        "data_fim_turma": datetime_legado(turma.get("data_fim")),
        "extinta": turma.get("extinta"),
    }


def montar_turmas_atribuidas_professor(codigo_rf: str) -> list[dict[str, Any]]:
    """Compõe as turmas atribuídas ao professor no recorte de etapa e tipo de UE.

    Args:
        codigo_rf: Registro funcional do professor.

    Returns:
        Linhas em snake_case prontas para serialização.
    """
    ancoras = get_turmas_professor(codigo_rf) or []
    if not isinstance(ancoras, list) or not ancoras:
        return []

    codigos_turma = sorted(
        {
            a["codigo_turma"]
            for a in ancoras
            if isinstance(a, dict) and a.get("codigo_turma") is not None
        }
    )
    codigos_ue = sorted(
        {
            a["codigo_unidade_educacao"]
            for a in ancoras
            if isinstance(a, dict) and a.get("codigo_unidade_educacao")
        }
    )
    if not codigos_turma or not codigos_ue:
        return []

    turmas = pedagogico_services.get_turmas_recorte_fund_medio_eja(
        codigos_turma
    )
    ues = institucional_services.get_ues_recorte_fund_medio(codigos_ue)
    turma_por_codigo = {
        t["codigo"]: t for t in turmas if isinstance(t, dict) and "codigo" in t
    }
    ue_por_codigo = {
        u["codigo"]: u for u in ues if isinstance(u, dict) and "codigo" in u
    }

    saida: list[dict[str, Any]] = []
    for ancora in ancoras:
        if not isinstance(ancora, dict):
            continue
        turma = turma_por_codigo.get(ancora.get("codigo_turma"))
        ue = ue_por_codigo.get(ancora.get("codigo_unidade_educacao"))
        if turma is None or ue is None:
            continue
        saida.append(_montar_turma_atribuida(ancora, turma, ue))
    return saida


def get_professor_por_rf_dre_ue(
    codigo_rf: str,
    ano_letivo: int,
    params: dict[str, str | list[str]] | None = None,
) -> Any:
    """Retorna professor por RF, DRE e UE no ano letivo.

    Args:
        codigo_rf: RF usado na consulta.
        ano_letivo: Ano letivo de referência.
        params: Filtros opcionais (dre_id, ue_id, buscar_outros_cargos).

    Returns:
        Dados do professor ou ausência de conteúdo.
    """
    path = f"{_BASE}/{codigo_rf}/BuscarPorRfDreUe/{ano_letivo}"
    resp = _client.get(path, params=params or None)
    return _client.json_or_none(resp)


def get_professores_por_lista_rf_ano(
    ano_letivo: int,
    codigos_rf: list[str],
) -> list[dict[str, Any]]:
    """Retorna professores pelos RFs no ano, no recorte de tipo de escola.

    Orquestra Professores e Institucional.
    o domínio Professores entrega os RFs com atribuição vigente no ano e as
    UEs dessas atribuições; o Institucional informa quais UEs estão no recorte
    do perfil de professor; o professor entra quando ao menos uma de suas UEs
    está no recorte (interseção).

    Args:
        ano_letivo: Ano letivo de referência.
        codigos_rf: RFs usados na consulta.

    Returns:
        Lista de ``{codigo_rf, nome}`` no recorte, ou lista vazia.
    """
    resp = _client.post(
        f"{_BASE}/{ano_letivo}/BuscarPorListaRF/",
        payload=codigos_rf,
    )
    candidatos = _client.json_or_none(resp) or []
    if not isinstance(candidatos, list) or not candidatos:
        return []

    todas_ues = sorted(
        {
            ue
            for cand in candidatos
            if isinstance(cand, dict)
            for ue in cand.get("codigos_ue", [])
        }
    )
    if not todas_ues:
        return []
    ues_recorte = set(
        institucional_services.get_codigos_ue_tipo_sgp(todas_ues)
    )
    return [
        {"codigo_rf": cand["codigo_rf"], "nome": cand["nome"]}
        for cand in candidatos
        if isinstance(cand, dict)
        and any(ue in ues_recorte for ue in cand.get("codigos_ue", []))
    ]


def get_unidades_atribuicao_professor(codigo_rf: str) -> list[str]:
    """Lista as UEs com atribuição válida do professor (domínio Professores).

    Args:
        codigo_rf: RF usado na consulta.

    Returns:
        Códigos EOL das unidades com atribuição válida.
    """
    resp = _client.get(f"{_BASE}/{codigo_rf}/unidades-atribuicao/")
    data = _client.json_or_none(resp) or {}
    return data.get("codigos_ue", []) if isinstance(data, dict) else []


def get_eh_emei(codigo_rf: str) -> bool:
    """Indica se o professor é EMEI orquestrando Professores e Institucional.

    O domínio Professores entrega as UEs com atribuição válida;
    o Institucional informa quais dessas UEs são EMEI.
    O vínculo existe quando a interseção não é vazia.

    Args:
        codigo_rf: RF usado na consulta.

    Returns:
        ``True`` quando o professor tem atribuição válida em unidade EMEI.
    """
    codigos_ue = get_unidades_atribuicao_professor(codigo_rf)
    if not codigos_ue:
        return False
    return bool(institucional_services.get_codigos_ue_emei(codigos_ue))


def get_autocomplete_professores(
    ano_letivo: int,
    dre_id: str,
    params: dict[str, str | list[str]] | None = None,
) -> Any:
    """Lista professores para autocomplete por DRE e ano.

    Args:
        ano_letivo: Ano letivo de referência.
        dre_id: Identificador da DRE usado na consulta.
        params: Filtros opcionais (ue_id, nome).

    Returns:
        Lista de professores ou ausência de conteúdo.
    """
    path = f"{_BASE}/{ano_letivo}/AutoComplete/{dre_id}"
    resp = _client.get(path, params=params or None)
    return _client.json_or_none(resp)


def get_turmas_professor_disciplina(
    codigo_rf: str,
    disciplina_id: str,
    codigos_turma: list[str],
) -> Any:
    """Retorna turmas do professor para a disciplina.

    Args:
        codigo_rf: RF usado na consulta.
        disciplina_id: Disciplina usada como filtro.
        codigos_turma: Turmas consideradas na consulta.

    Returns:
        Lista de turmas atribuídas ou ausência de conteúdo.
    """
    resp = _client.post(
        f"{_BASE}/{codigo_rf}/disciplina/{disciplina_id}/turmas/",
        payload=codigos_turma,
    )
    return _client.json_or_none(resp)
