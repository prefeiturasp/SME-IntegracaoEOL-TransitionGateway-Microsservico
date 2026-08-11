"""Serviços de integração do domínio professores."""

from collections.abc import Iterable
from datetime import date, datetime
from typing import Any, cast

from apps.core.api_clients import get_api_client
from apps.core.datetime import (
    datetime_de_tick,
    datetime_legado,
    obter_ano_tick,
)
from apps.institucional import services as institucional_services
from apps.pedagogico import services as pedagogico_services

_BASE = "/api/v1/professores"
_BASE_ACESSOS = f"{_BASE}/acessos"
_BASE_FUNCIONARIOS = f"{_BASE}/funcionarios"
_BASE_FUNCIONARIOS_LEGADO = "/api/v1/funcionarios"
_BASE_ESCOLAS = f"{_BASE}/escolas"
_BASE_TURMAS = f"{_BASE}/turmas"
_TIPO_ABRANGENCIA_UE = 1
_TIPO_ABRANGENCIA_PROFESSOR = 2
_TIPO_ABRANGENCIA_UE_TURMAS_DISCIPLINAS = 3
_TIPO_ABRANGENCIA_DRE = 4
_TIPO_ABRANGENCIA_DRE_ESCOLAS_ATRIBUIDAS = 5
_TIPO_ABRANGENCIA_SME = 6
_TIPOS_ABRANGENCIA_DRE = frozenset(
    {_TIPO_ABRANGENCIA_DRE, _TIPO_ABRANGENCIA_DRE_ESCOLAS_ATRIBUIDAS}
)
_TIPOS_ABRANGENCIA_VINCULO_UE = frozenset(
    {
        _TIPO_ABRANGENCIA_UE,
        _TIPO_ABRANGENCIA_UE_TURMAS_DISCIPLINAS,
        _TIPO_ABRANGENCIA_DRE,
        _TIPO_ABRANGENCIA_DRE_ESCOLAS_ATRIBUIDAS,
    }
)

_COMPONENTE_AGRUPAMENTO_TERRITORIO_SABER_ID_INICIAL = 800000

_client = get_api_client("professores")


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


def _codigos_ue(data: Any) -> list[str]:
    """Extrai códigos de UE dos dados recebidos.

    Args:
        data: Dados consultados.

    Returns:
        Códigos EOL das unidades educacionais.
    """
    if not isinstance(data, dict):
        return []
    codigos = data.get("codigos_ue")
    if not isinstance(codigos, list):
        return []
    return [codigo for codigo in codigos if isinstance(codigo, str)]


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
    nome_param_destino: str | None = None,
) -> Any:
    """Lista funcionários de escola para cada valor de filtro.

    Args:
        codigo_ue: Código da unidade escolar usada na consulta.
        params: Parâmetros recebidos para a consulta.
        nome_param: Nome do filtro recebido.
        nome_campo: Campo preenchido com o valor do filtro.
        nome_param_destino: Nome usado ao encaminhar o filtro.

    Returns:
        Lista consolidada de funcionários encontrados.

    Raises:
        ValueError: Quando algum valor do filtro não for numérico.
    """
    path = f"{_BASE_ESCOLAS}/{codigo_ue}/funcionarios/"
    valores = _valores_param(params, nome_param)
    if not valores:
        return []

    nome_destino = nome_param_destino or nome_param
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


def get_codigos_turmas_historicas_professor(
    ano_letivo: int,
    professor_rf: str,
) -> list[int]:
    """Lista códigos de turmas históricas do professor no ano letivo.

    Args:
        ano_letivo: Ano letivo usado na consulta.
        professor_rf: Registro funcional do professor.

    Returns:
        Códigos de turma sem duplicidade.

    Raises:
        ValueError: Se a resposta não contiver códigos inteiros.
    """
    resp = _client.get(
        f"{_BASE_TURMAS}/anos-letivos/{ano_letivo}/professor/"
        f"{professor_rf}/turmas-historicas-geral/"
    )
    if resp.status_code == 404:
        return []
    resp.raise_for_status()
    payload = _client.json_or_none(resp)
    if not isinstance(payload, list):
        raise ValueError(
            "Resposta de turmas históricas deve conter códigos inteiros."
        )

    codigos: list[int] = []
    codigos_incluidos: set[int] = set()
    for item in payload:
        codigo = item.get("codigo") if isinstance(item, dict) else item
        if not isinstance(codigo, int) or isinstance(codigo, bool):
            raise ValueError(
                "Resposta de turmas históricas deve conter códigos inteiros."
            )
        if codigo not in codigos_incluidos:
            codigos.append(codigo)
            codigos_incluidos.add(codigo)
    return codigos


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


def get_funcionario_externo(cpf: str) -> Any:
    """Retorna funcionario externo por CPF.

    Args:
        cpf: CPF usado na consulta.

    Returns:
        Lista de funcionarios externos ou ausencia de dados.
    """
    resp = _client.get(f"{_BASE_FUNCIONARIOS}/funcionario-externo/{cpf}/")
    return _client.json_or_none(resp)


def get_funcionarios_por_lista_login(logins: list[str]) -> Any:
    """Retorna funcionarios pelos logins informados.

    Args:
        logins: Logins usados na consulta.

    Returns:
        Lista de funcionarios ou ausencia de dados.
    """
    resp = _client.post(
        f"{_BASE_FUNCIONARIOS}/BuscarPorListaLogin/",
        payload=logins,
    )
    return _client.json_or_none(resp)


def get_funcionarios_unidade(codigo_dre_ue: str, perfis: list[str]) -> Any:
    """Retorna funcionarios por unidade e perfis.

    Args:
        codigo_dre_ue: Codigo da unidade ou DRE/UE usada na consulta.
        perfis: Identificadores de perfis usados na consulta.

    Returns:
        Funcionarios encontrados ou ausencia de dados.
    """
    resp = _client.post(
        f"{_BASE_FUNCIONARIOS}/unidade/{codigo_dre_ue}/",
        payload=perfis,
    )
    return _client.json_or_none(resp)


def get_funcionarios_admins_sme(perfis: list[str]) -> Any:
    """Retorna administradores SME pelos perfis informados.

    Args:
        perfis: Identificadores de perfis usados na consulta.

    Returns:
        Lista de RFs/logins dos administradores ou ausencia de dados.
    """
    resp = _client.post(
        f"{_BASE_FUNCIONARIOS}/admins/sme/",
        payload=perfis,
    )
    return _client.json_or_none(resp)


def get_funcionario_dados_sigpae(codigo_rf: str) -> Any:
    """Retorna dados SIGPAE do funcionario.

    Args:
        codigo_rf: RF usado na consulta.

    Returns:
        Dados SIGPAE do funcionario ou ausencia de dados.
    """
    resp = _client.get(f"{_BASE_FUNCIONARIOS}/DadosSigpae/{codigo_rf}/")
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


def get_funcionarios_ue(codigo_ue: str, payload: dict[str, Any]) -> Any:
    """Retorna funcionários vinculados à unidade educacional.

    Args:
        codigo_ue: Código da unidade educacional usada na consulta.
        payload: Filtros enviados no contrato legado.

    Returns:
        Lista de funcionários da unidade ou ausência de conteúdo.
    """
    resp = _client.post(
        f"{_BASE_FUNCIONARIOS}/ue/{codigo_ue}/",
        payload=payload,
    )
    return _client.json_or_none(resp)


def get_funcionarios_por_cargo(codigo_cargo: str) -> Any:
    """Retorna funcionários vinculados ao cargo.

    Args:
        codigo_cargo: Código do cargo usado na consulta.

    Returns:
        Lista de funcionários do cargo ou ausência de conteúdo.
    """
    resp = _client.get(f"{_BASE_FUNCIONARIOS}/cargos/{codigo_cargo}/")
    return _client.json_or_none(resp)


def get_cargos_funcionario(registro_funcional: str) -> Any:
    """Retorna cargos por registro funcional.

    Args:
        registro_funcional: RF usado na consulta.

    Returns:
        Vínculos funcionais encontrados ou ausência de conteúdo.
    """
    resp = _client.get(f"{_BASE_FUNCIONARIOS}/cargo/{registro_funcional}/")
    return _client.json_or_none(resp)


def get_funcionarios_conecta_formacao(
    params: dict[str, str | list[str]],
) -> Any:
    """Retorna funcionários elegíveis para o Conecta Formação.

    Args:
        params: Filtros recebidos na consulta.

    Returns:
        Funcionários encontrados ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS}/registros-funcionais/conecta-formacao/",
        params=params or None,
    )
    return _client.json_or_none(resp)


def get_dre_ue_atribuicao_cargo(
    registro_funcional: str,
    codigo_cargo: str,
) -> Any:
    """Retorna DRE e UE da atribuição por cargo.

    Args:
        registro_funcional: RF usado na consulta.
        codigo_cargo: Código do cargo usado na consulta.

    Returns:
        Vínculos encontrados ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS}/atribuicao/{registro_funcional}/"
        f"cargo/{codigo_cargo}/"
    )
    return _client.json_or_none(resp)


def get_usuarios_conecta_formacao(perfis: list[str]) -> Any:
    """Retorna usuários do Conecta Formação por perfis.

    Args:
        perfis: Perfis usados na consulta.

    Returns:
        Usuários encontrados ou ausência de conteúdo.
    """
    resp = _client.post(
        f"{_BASE_FUNCIONARIOS}/usuarios/conecta-formacao/",
        payload=perfis,
    )
    return _client.json_or_none(resp)


def get_supervisores_por_dre(
    codigo_dre: str,
    codigos_supervisores: list[str],
) -> Any:
    """Retorna supervisores vinculados à DRE.

    Args:
        codigo_dre: Código EOL da DRE consultada.
        codigos_supervisores: Registros funcionais considerados na busca.

    Returns:
        Lista de supervisores ou ausência de conteúdo.
    """
    resp = _client.post(
        f"{_BASE_FUNCIONARIOS}/supervisores/{codigo_dre}/",
        payload=codigos_supervisores,
    )
    return _client.json_or_none(resp)


def get_supervisores_dre(codigo_eol_dre: str) -> Any:
    """Retorna supervisores vinculados a DRE.

    Args:
        codigo_eol_dre: Codigo EOL da DRE consultada.

    Returns:
        Lista de supervisores ou ausencia de dados.
    """
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS}/dres/{codigo_eol_dre}/supervisores/"
    )
    return _client.json_or_none(resp)


def get_usuarios_sgp_por_perfil(
    id_perfil: str,
    params: dict[str, Any],
) -> Any:
    """Retorna usuários SGP por perfil.

    Args:
        id_perfil: Perfil usado na consulta.
        params: Filtros enviados no contrato legado.

    Returns:
        Usuários SGP encontrados ou erro de contrato.
    """
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS}/perfis/{id_perfil}/",
        params=params or None,
    )
    return _client.json_or_none(resp)


def get_funcionarios_sgp_por_perfil_dre(
    id_perfil: str,
    codigo_dre: str,
    params: dict[str, Any],
) -> Any:
    """Retorna funcionários SGP por perfil e DRE.

    Args:
        id_perfil: Perfil usado na consulta.
        codigo_dre: DRE usada na consulta.
        params: Filtros enviados no contrato legado.

    Returns:
        Funcionários SGP encontrados ou erro de contrato.
    """
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS}/perfis/{id_perfil}/dres/{codigo_dre}/",
        params=params or None,
    )
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


def get_disciplinas_turma(codigo_turma: str) -> Any:
    """Retorna disciplinas de uma turma.

    Args:
        codigo_turma: Código da turma usada na consulta.

    Returns:
        Disciplinas retornadas pela fonte pedagógica.
    """
    data = pedagogico_services.get_componentes_por_lista_turmas(
        [codigo_turma],
        adicionar_componentes_planejamento=False,
        incluir_extintas=True,
    )
    return data


def get_disciplinas_funcionario_turma(
    login: str,
    id_perfil: str,
    codigo_turma: str,
    planejamento: bool = False,
    abrangencia: int | None = None,
    cargos: list[int] | None = None,
) -> Any:
    """Retorna disciplinas do funcionário em uma turma.

    Args:
        login: Login/RF usado na consulta.
        id_perfil: Perfil usado na consulta.
        codigo_turma: Código da turma usada na consulta.
        planejamento: Indica consulta para planejamento.
        abrangencia: Tipo de abrangência temporário; substitui o valor que
            viria da identidade enquanto a integração não existe.
        cargos: Cargos temporários do perfil usados no filtro de vínculo.

    Returns:
        Disciplinas retornadas pela fonte selecionada.
    """
    data = _get_componentes_por_switch(
        login=login,
        id_perfil=id_perfil,
        codigo_turma=codigo_turma,
        planejamento=planejamento,
        abrangencia=abrangencia,
        cargos=cargos,
    )
    return data


def _get_componentes_por_switch(
    login: str,
    id_perfil: str,
    codigo_turma: str,
    planejamento: bool,
    abrangencia: int | None = None,
    cargos: list[int] | None = None,
) -> Any:
    """Seleciona a fonte de componentes pela abrangência.

    ``abrangencia`` é o override temporário informado na consulta até a
    integração com identidade; sem ele, cai na fonte padrão do funcionário.
    """
    tipo_abrangencia = abrangencia

    if tipo_abrangencia == _TIPO_ABRANGENCIA_PROFESSOR:
        return _get_componentes_professor(
            login,
            id_perfil,
            codigo_turma,
            planejamento,
        )

    if tipo_abrangencia in _TIPOS_ABRANGENCIA_VINCULO_UE:
        return _get_componentes_turma_atribuida_ue(
            login,
            id_perfil,
            codigo_turma,
            planejamento,
            cargos=cargos,
        )

    if tipo_abrangencia == _TIPO_ABRANGENCIA_SME:
        return _get_componentes_sme(codigo_turma, planejamento)

    return _get_componentes_funcionario(
        login,
        id_perfil,
        codigo_turma,
        planejamento,
    )


def _get_componentes_professor(
    login: str,
    id_perfil: str,
    codigo_turma: str,
    planejamento: bool,
) -> Any:
    """Consulta componentes do professor."""
    return _get_componentes_funcionario(
        login,
        id_perfil,
        codigo_turma,
        planejamento,
    )


def _get_componentes_turma_atribuida_ue(
    login: str,
    id_perfil: str,
    codigo_turma: str,
    planejamento: bool,
    cargos: list[int] | None = None,
) -> Any:
    """Consulta disciplinas por vínculo de UE."""
    if planejamento:
        return _get_componentes_funcionario(
            login,
            id_perfil,
            codigo_turma,
            planejamento,
        )

    params: dict[str, Any] = {}
    if cargos:
        params["cargos"] = [str(cargo) for cargo in cargos]

    resp = _client.get(
        f"{_BASE_FUNCIONARIOS_LEGADO}/{login}/turmas/"
        f"{codigo_turma}/disciplinas-atribuidas-ue/",
        params=params or None,
    )
    return _client.json_or_none(resp)


def _get_componentes_sme(codigo_turma: str, planejamento: bool) -> Any:
    """Consulta componentes da turma."""
    return pedagogico_services.get_componentes_por_lista_turmas(
        [codigo_turma],
        adicionar_componentes_planejamento=planejamento,
    )


def _get_componentes_funcionario(
    login: str,
    id_perfil: str,
    codigo_turma: str,
    planejamento: bool,
) -> Any:
    """Consulta componentes do funcionário no domínio pedagógico."""
    if planejamento:
        return pedagogico_services.get_componentes_planejamento(
            codigo_turma=codigo_turma,
            login=login,
            id_perfil=id_perfil,
        )
    return pedagogico_services.get_componentes_turma_funcionario(
        codigo_turma=codigo_turma,
        login=login,
        id_perfil=id_perfil,
        agrupa_componente_curricular=False,
    )


def get_abrangencia_funcionario_perfil(
    login: str,
    id_perfil: str,
    abrangencia: int | None = None,
    cargos: list[int] | None = None,
    funcoes: list[int] | None = None,
    grupo: int | None = None,
    dre_codigo: str | None = None,
    eh_perfil_manual: bool = False,
) -> Any:
    """Retorna abrangência de turmas do funcionário.

    Args:
        login: Login usado na consulta.
        id_perfil: Perfil usado na consulta.
        abrangencia: Tipo de abrangência temporário; substitui o valor que
            viria da identidade enquanto a integração não existe.
        cargos: Cargos temporários do perfil usados no filtro de vínculo.
        funcoes: Funções temporárias do perfil.
        grupo: Grupo temporário do perfil.
        dre_codigo: DRE temporária usada na abrangência por DRE.
        eh_perfil_manual: Marca temporária de perfil manual no bloco.

    Returns:
        Abrangência de turmas ou ausência de conteúdo.
    """
    if abrangencia == _TIPO_ABRANGENCIA_SME:
        data = get_todas_turmas_atribuidas_dre_ue()
    elif abrangencia == _TIPO_ABRANGENCIA_PROFESSOR:
        data = montar_turmas_atribuidas_professor(login)
    elif abrangencia in _TIPOS_ABRANGENCIA_VINCULO_UE:
        dre = dre_codigo if abrangencia in _TIPOS_ABRANGENCIA_DRE else None
        cargos_filtro = (
            None if abrangencia in _TIPOS_ABRANGENCIA_DRE else cargos
        )
        data = get_turmas_atribuidas_ue(login, cargos_filtro, dre)
    else:
        resp = _client.get(
            f"{_BASE_FUNCIONARIOS_LEGADO}/{login}/perfis/{id_perfil}/turmas/"
        )
        data = _client.json_or_none(resp)
    return data


def get_turmas_atribuidas_ue(
    codigo_rf: str,
    cargos: list[int] | None = None,
    codigo_dre: str | None = None,
) -> Any:
    """Retorna turmas atribuídas por vínculo com UE.

    Args:
        codigo_rf: RF usado na consulta.
        cargos: Cargos usados no filtro.
        codigo_dre: DRE usada no filtro.

    Returns:
        Turmas atribuídas por vínculo com UE.
    """
    params: dict[str, Any] = {}
    if cargos:
        params["cargos"] = [str(cargo) for cargo in cargos]
    if codigo_dre:
        params["codigo_dre"] = codigo_dre
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS_LEGADO}/{codigo_rf}/turmas-atribuidas-ue/",
        params=params or None,
    )
    data = _client.json_or_none(resp)
    return data


def get_abrangencia_ues(codigos_ue: list[str]) -> Any:
    """Retorna abrangência de turmas para unidades.

    Args:
        codigos_ue: Códigos EOL das unidades educacionais.

    Returns:
        Abrangência de turmas ou ausência de conteúdo.
    """
    data = pedagogico_services.get_turmas_atribuidas_dre_ue(codigos_ue)
    return data


def get_todas_turmas_atribuidas_dre_ue() -> Any:
    """Retorna abrangência de turmas atribuídas (já agrupada pelo domínio)."""
    return pedagogico_services.get_todas_turmas_atribuidas_dre_ue()


def get_turmas_elegiveis(payload: dict[str, Any]) -> Any:
    """Retorna turmas elegíveis para cópia.

    Args:
        payload: Dados usados na consulta.

    Returns:
        Turmas elegíveis ou ausência de conteúdo.
    """
    data = pedagogico_services.get_turmas_elegiveis(payload)
    return data


def get_funcionarios(payload: dict[str, Any]) -> Any:
    """Retorna funcionários por filtros básicos.

    Args:
        payload: Filtros recebidos na requisição.

    Returns:
        Funcionários encontrados ou ausência de conteúdo.
    """
    resp = _client.post(
        f"{_BASE_FUNCIONARIOS_LEGADO}/",
        payload=payload,
    )
    data = _client.json_or_none(resp)
    return data


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
    """Compõe turmas atribuídas no recorte de etapa e tipo de UE.

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
    """Retorna professores pelos RFs no ano, um item por turma atribuída.

    Args:
        ano_letivo: Ano letivo de referência.
        codigos_rf: RFs usados na consulta.

    Returns:
        Lista de ``{codigo_rf, nome}`` com um item por turma, ou lista vazia.
    """
    resp = _client.post(
        f"{_BASE}/{ano_letivo}/BuscarPorListaRF/",
        payload=codigos_rf,
    )
    resultado = _client.json_or_none(resp)
    if not isinstance(resultado, list):
        return []
    return resultado


def get_unidades_atribuicao_professor(codigo_rf: str) -> list[str]:
    """Lista as UEs com atribuição válida do professor (domínio Professores).

    Args:
        codigo_rf: RF usado na consulta.

    Returns:
        Códigos EOL das unidades com atribuição válida.
    """
    resp = _client.get(f"{_BASE}/{codigo_rf}/unidades-atribuicao/")
    return _codigos_ue(_client.json_or_none(resp))


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


def buscar_professores_titulares_por_turma(
    codigo_turma: str,
    data_referencia: datetime | None,
    realiza_agrupamento: bool,
) -> list[dict[str, Any]]:
    """Busca professores titulares de uma turma.

    Args:
        codigo_turma: Código da turma consultada.
        data_referencia: Data de referência usada como filtro opcional.
        realiza_agrupamento: Indica se componentes devem ser agrupados.

    Returns:
        Professores titulares encontrados ou uma lista vazia.

    Raises:
        httpx.HTTPError: Quando a chamada ao serviço de professores falha.
        ValueError: Quando a resposta não pode ser convertida para JSON.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_turma}/titulares/",
    )
    payload = _client.json_or_none(resp)
    if not isinstance(payload, list):
        return []

    componentes_professor = [
        item for item in payload if isinstance(item, dict)
    ]

    componentes_api_eol = pedagogico_services.get_componentes_api_eol()

    _verifica_se_existe_vigencia_ativa = next(
        (
            _verificar_vigencia_componente_pai(
                componentes_api_eol,
                str(componente.get("disciplina_id")),
                data_referencia,
            )
            for componente in componentes_professor
        ),
        False,
    )

    atribuicoes_turma_territorio_saber = (
        pedagogico_services.get_professores_turma_territorio_saber(
            codigo_turma
        )
    )
    if isinstance(atribuicoes_turma_territorio_saber, list) and any(
        atribuicoes_turma_territorio_saber
    ):
        componentes_professor = _tratar_agrupamento_componentes_professor(
            codigo_turma,
            componentes_professor,
            atribuicoes_turma_territorio_saber,
        )

    componentes_retorno: list[dict[str, Any]] = []
    if realiza_agrupamento or _verifica_se_existe_vigencia_ativa:
        componentes_retorno = [
            _montar_componente_professor_agrupado(
                componente,
                componentes_api_eol,
            )
            for componente in componentes_professor
        ]
    else:
        componentes_retorno = componentes_professor

    _aplicar_descricoes_componentes_turma(
        codigo_turma,
        componentes_retorno,
    )

    componentes_agrupados = _agrupar_componentes_retorno(componentes_retorno)
    return [
        componente
        for componente in componentes_agrupados
        if _possui_dados_professor_titular(componente)
    ]


def _aplicar_descricoes_componentes_turma(
    codigo_turma: str,
    componentes_retorno: list[dict[str, Any]],
) -> None:
    """Aplica descrições territoriais aos componentes de uma turma.

    Args:
        codigo_turma: Código da turma consultada.
        componentes_retorno: Componentes que receberão as descrições.
    """
    componentes_codigos = [
        str(componente["disciplina_id"])
        for componente in componentes_retorno
        if componente.get("disciplina_id") is not None
        and str(componente["disciplina_id"]).strip()
        and str(componente["disciplina_id"]).strip().lower() != "none"
    ]

    componentes_turmas = pedagogico_services.get_turma_componentes_turma(
        codigo_turma,
        componentes_codigos,
    )

    if isinstance(componentes_turmas, list):
        for componente_retorno in componentes_retorno:
            componente_turma = next(
                (
                    componente
                    for componente in componentes_turmas
                    if isinstance(componente, dict)
                    and str(componente.get("componente_codigo"))
                    == str(componente_retorno.get("disciplina_id"))
                    and componente.get("desc_experiencia_pedagogica")
                    is not None
                ),
                None,
            )
            if (
                componente_turma is not None
                and componente_turma.get("desc_experiencia_pedagogica")
                is not None
            ):
                descricao_territorio = componente_turma.get(
                    "desc_territorio_saber"
                )
                descricao_experiencia = componente_turma[
                    "desc_experiencia_pedagogica"
                ]
                componente_retorno["disciplina"] = " - ".join(
                    descricao
                    for descricao in (
                        descricao_territorio,
                        descricao_experiencia,
                    )
                    if descricao
                )


def _possui_dados_professor_titular(componente: dict[str, Any]) -> bool:
    """Verifica se o componente possui dados relevantes para o retorno.

    Args:
        componente: Dados agrupados do professor e componente curricular.

    Returns:
        True quando ao menos um campo relevante está preenchido.
    """
    campos_relevantes = (
        "professor_rf",
        "nome_professor",
        "disciplina",
        "disciplina_id",
        "disciplinas_id",
    )
    return any(
        valor is not None
        and str(valor).strip()
        and str(valor).strip().lower() != "none"
        for valor in (componente.get(campo) for campo in campos_relevantes)
    )


def buscar_professores_titulares_por_ue(
    ue_codigo: str,
    data_referencia: datetime,
    realiza_agrupamento: bool,
) -> list[dict[str, Any]]:
    """Busca professores titulares de uma UE na data de referência.

    Args:
        ue_codigo: Código da unidade educacional consultada.
        data_referencia: Data usada para consultar as atribuições vigentes.
        realiza_agrupamento: Indica se os componentes devem ser agrupados.

    Returns:
        Professores titulares encontrados ou uma lista vazia.

    Raises:
        httpx.HTTPError: Quando a chamada ao serviço de professores falha.
        ValueError: Quando a resposta não pode ser convertida para JSON.
    """
    resp = _client.get(
        f"{_BASE}/titulares/ue/{ue_codigo}/"
        f"{data_referencia.date().isoformat()}"
    )
    payload = _client.json_or_none(resp)
    if not isinstance(payload, list):
        return []

    componentes_professor = [
        item for item in payload if isinstance(item, dict)
    ]
    if not componentes_professor:
        return []

    componentes_api_eol = pedagogico_services.get_componentes_api_eol()

    existe_vigencia_ativa = any(
        _verificar_vigencia_componente_pai(
            componentes_api_eol,
            str(componente.get("disciplina_id")),
            data_referencia,
        )
        for componente in componentes_professor
    )

    codigos_turmas = _valores_distintos(
        componente.get("turma_id") for componente in componentes_professor
    )
    if codigos_turmas:
        atribuicoes_turma_territorio_saber = (
            pedagogico_services.get_professores_turmas_territorio_saber(
                codigos_turmas
            )
        )
        if isinstance(atribuicoes_turma_territorio_saber, list) and any(
            atribuicoes_turma_territorio_saber
        ):
            componentes_professor = _tratar_agrupamento_componentes_professor(
                codigos_turmas,
                componentes_professor,
                atribuicoes_turma_territorio_saber,
            )

    if realiza_agrupamento or existe_vigencia_ativa:
        componentes_retorno = [
            _montar_componente_professor_agrupado(
                componente,
                componentes_api_eol,
            )
            for componente in componentes_professor
        ]
    else:
        componentes_retorno = componentes_professor

    for codigo_turma in codigos_turmas:
        componentes_turma = [
            componente
            for componente in componentes_retorno
            if str(componente.get("turma_id")) == codigo_turma
        ]
        _aplicar_descricoes_componentes_turma(
            codigo_turma,
            componentes_turma,
        )

    return componentes_retorno


def buscar_professor_titular_por_turma_disciplina(
    codigo_turma: str,
    codigo_componente_curricular: str,
) -> dict[str, Any] | None:
    """Busca o professor titular da turma e componente curricular.

    Args:
        codigo_turma: Código da turma consultada.
        codigo_componente_curricular: Código do componente curricular.

    Returns:
        Professor titular encontrado ou ausência de conteúdo.

    Raises:
        httpx.HTTPError: Quando a chamada ao serviço de professores falha.
        ValueError: Quando a resposta não pode ser convertida para JSON.
    """
    if _validar_componente_eh_territorio_saber_agrupado(
        codigo_componente_curricular
    ):
        atribuicoes_territorio_saber = (
            pedagogico_services.get_professores_turma_territorio_saber(
                codigo_turma
            )
        )
        componente_professor = next(
            (
                componente
                for componente in atribuicoes_territorio_saber
                if isinstance(componente, dict)
                and str(componente.get("disciplina_id"))
                == codigo_componente_curricular
            ),
            None,
        )
        if componente_professor is None:
            return None
        disciplinas_agrupadas = componente_professor.get(
            "disciplinas_agrupadas_ids"
        )
        return {
            "disciplina": componente_professor.get("disciplina_nome"),
            "disciplina_id": str(componente_professor.get("disciplina_id")),
            "disciplinas_id": ",".join(
                str(disciplina_id)
                for disciplina_id in disciplinas_agrupadas or []
            ),
            "nome_professor": componente_professor.get("nome_professor"),
            "professor_rf": componente_professor.get("codigo_rf"),
            "turma_id": int(cast(Any, componente_professor["codigo_turma"])),
        }

    resp = _client.get(
        f"{_BASE}/titular/turmas/{codigo_turma}/"
        f"componentes-curriculares/{codigo_componente_curricular}"
    )
    payload = _client.json_or_none(resp)
    if not isinstance(payload, dict):
        return None

    disciplina_id = payload.get("disciplina_id")
    componentes_turma = pedagogico_services.get_turma_componentes_turma(
        codigo_turma,
        [str(disciplina_id)],
    )
    if isinstance(componentes_turma, list):
        componente_turma = next(
            (
                componente
                for componente in componentes_turma
                if isinstance(componente, dict)
                and str(componente.get("componente_codigo"))
                == str(disciplina_id)
                and componente.get("desc_experiencia_pedagogica") is not None
            ),
            None,
        )
        if componente_turma is not None:
            payload["disciplina"] = componente_turma[
                "desc_experiencia_pedagogica"
            ]

    return payload


def _agrupar_componentes_retorno(
    componentes_retorno: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Agrupa componentes por disciplina e RF do professor.

    Args:
        componentes_retorno: Componentes tratados que serão agrupados.

    Returns:
        Componentes no contrato interno do DTO de professor titular.
    """
    grupos: dict[tuple[Any, Any], list[dict[str, Any]]] = {}
    for componente in componentes_retorno:
        chave = (
            componente.get("disciplina"),
            componente.get("professor_rf"),
        )
        grupos.setdefault(chave, []).append(componente)

    retorno: list[dict[str, Any]] = []
    for componentes in grupos.values():
        primeiro = componentes[0]
        disciplinas_id = ",".join(
            (
                ""
                if componente.get("disciplina_id") is None
                else str(componente.get("disciplina_id"))
            )
            for componente in componentes
        )
        nomes_professores = ", ".join(
            _valores_distintos(
                componente.get("nome_professor") for componente in componentes
            )
        ).replace(", Não há professor titular.", "")
        professores_rf = ", ".join(
            _valores_distintos(
                componente.get("professor_rf") for componente in componentes
            )
        )
        retorno.append(
            {
                "disciplina": primeiro.get("disciplina"),
                "disciplina_id": primeiro.get("disciplina_id"),
                "disciplinas_id": disciplinas_id,
                "nome_professor": nomes_professores,
                "professor_rf": professores_rf,
                "turma_id": 0,
            }
        )

    return retorno


def _valores_distintos(valores: Iterable[Any]) -> list[str]:
    """Retorna representações textuais distintas na ordem original.

    Args:
        valores: Valores que serão deduplicados.

    Returns:
        Valores textuais distintos.
    """
    retorno: list[str] = []
    vistos: set[str] = set()
    for valor in valores:
        texto = "" if valor is None else str(valor)
        if texto not in vistos:
            vistos.add(texto)
            retorno.append(texto)
    return retorno


def _montar_componente_professor_agrupado(
    componente_professor: dict[str, Any],
    componentes_api_eol: list[dict[str, Any]],
) -> dict[str, Any]:
    """Monta o componente do professor usando os dados do componente pai.

    Args:
        componente_professor: Componente associado ao professor titular.
        componentes_api_eol: Componentes curriculares retornados pela API EOL.

    Returns:
        Componente no contrato interno de professor titular, agrupado pelo pai
        quando ele existir.
    """
    disciplina_id = str(componente_professor.get("disciplina_id"))
    componente_atual = next(
        (
            componente
            for componente in componentes_api_eol
            if isinstance(componente, dict)
            and str(componente.get("id_componente_curricular"))
            == disciplina_id
        ),
        None,
    )
    codigo_componente_pai = (
        componente_atual.get("id_componente_curricular_pai")
        if componente_atual is not None
        else None
    )
    componente_pai = next(
        (
            componente
            for componente in componentes_api_eol
            if isinstance(componente, dict)
            and codigo_componente_pai is not None
            and str(componente.get("id_componente_curricular"))
            == str(codigo_componente_pai)
        ),
        None,
    )

    return {
        "disciplina": (
            componente_pai.get("descricao")
            if componente_pai is not None
            else componente_professor.get("disciplina")
        ),
        "disciplina_id": (
            str(codigo_componente_pai)
            if codigo_componente_pai is not None
            else disciplina_id
        ),
        "disciplinas_id": None,
        "nome_professor": componente_professor.get("nome_professor"),
        "professor_rf": componente_professor.get("professor_rf"),
        "turma_id": componente_professor.get("turma_id", 0),
    }


def _tratar_agrupamento_componentes_professor(
    codigos_turmas: str | list[str],
    componentes_professor: list[dict[str, Any]],
    atribuicoes_territorio_saber: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Agrupa componentes regulares e atribuições de Território do Saber.

    Args:
        codigos_turmas: Códigos das turmas que serão tratados.
        componentes_professor: Componentes regulares dos professores
            titulares.
        atribuicoes_territorio_saber: Atribuições agrupadas de Território
            do Saber.

    Returns:
        Componentes regulares não agrupados e atribuições de Território do
        Saber convertidas para o contrato interno de professor titular.
    """
    turmas = (
        [codigos_turmas] if isinstance(codigos_turmas, str) else codigos_turmas
    )
    retorno: list[dict[str, Any]] = []

    for codigo_turma in turmas:
        ids_componentes_territorio = {
            int(disciplina_agrupada_id)
            for atribuicao in atribuicoes_territorio_saber
            if str(atribuicao.get("codigo_turma")) == codigo_turma
            for disciplina_agrupada_id in (
                atribuicao.get("disciplinas_agrupadas_ids") or []
            )
        }
        componentes_regulares = [
            componente
            for componente in componentes_professor
            if str(componente.get("turma_id")) == codigo_turma
            and int(cast(Any, componente.get("disciplina_id")))
            not in ids_componentes_territorio
        ]
        retorno.extend(componentes_regulares)
        retorno.extend(
            {
                "disciplina": atribuicao.get("disciplina_nome"),
                "disciplina_id": atribuicao.get("disciplina_id"),
                "disciplinas_id": atribuicao.get("disciplina_id"),
                "nome_professor": atribuicao.get("nome_professor")
                or next(
                    (
                        componente.get("nome_professor")
                        for componente in componentes_professor
                        if str(componente.get("professor_rf"))
                        == str(atribuicao.get("codigo_rf"))
                        and int(cast(Any, componente.get("disciplina_id")))
                        in ids_componentes_territorio
                    ),
                    None,
                ),
                "professor_rf": atribuicao.get("codigo_rf"),
                "turma_id": int(cast(Any, atribuicao.get("codigo_turma"))),
            }
            for atribuicao in atribuicoes_territorio_saber
            if str(atribuicao.get("codigo_turma")) == codigo_turma
        )

    return retorno


def get_turmas_atribuidas_professor_escola(
    codigo_rf: str,
    codigo_eol_escola: str,
    ano_letivo: int,
) -> Any:
    """Retorna turmas atribuídas ao professor na escola.

    Args:
        codigo_rf: RF usado na consulta.
        codigo_eol_escola: Código EOL da escola usada na consulta.
        ano_letivo: Ano letivo de referência.

    Returns:
        Lista de turmas atribuídas ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_rf}/escolas/{codigo_eol_escola}/"
        f"turmas/anos_letivos/{ano_letivo}/"
    )
    turmas = _client.json_or_none(resp)
    if not isinstance(turmas, list):
        return []

    saida: list[dict[str, Any]] = []

    for turma in turmas:
        saida.append(_montar_turma_atribuida_professor_escola(turma))

    return saida


def get_turmas_atribuidas_professores_escola(
    codigo_eol_escola: str,
    ano_letivo: int,
) -> Any:
    """Retorna turmas atribuídas aos professores na escola.

    Args:
        codigo_eol_escola: Código EOL da escola usada na consulta.
        ano_letivo: Ano letivo de referência.

    Returns:
        Lista de turmas atribuídas ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE}/escolas/{codigo_eol_escola}/"
        f"turmas/anos_letivos/{ano_letivo}/"
    )
    turmas = _client.json_or_none(resp)
    if not isinstance(turmas, list):
        return []

    saida: list[dict[str, Any]] = []

    for turma in turmas:
        saida.append(_montar_turma_atribuida_professor_escola(turma))

    return saida


def get_professores_escola(
    codigo_eol_escola: str,
    ano_letivo: int = 0,
) -> Any:
    """Retorna professores atribuídos a uma escola.

    Args:
        codigo_eol_escola: Código EOL da escola usada na consulta.
        ano_letivo: Ano letivo usado para filtrar as atribuições.

    Returns:
        Lista de professores retornada pelo domínio.
    """
    resp = _client.get(
        f"{_BASE}/escolas/{codigo_eol_escola}/professores/{ano_letivo}/"
    )
    data = _client.json_or_none(resp)
    if not isinstance(data, list):
        return []
    return data


def get_turmas_atribuidas_professor(
    codigo_rf: str,
    ano_letivo: int,
) -> Any:
    """Retorna turmas atribuídas ao professor no ano letivo.

    Args:
        codigo_rf: RF usado na consulta.
        ano_letivo: Ano letivo de referência.

    Returns:
        Lista de turmas atribuídas ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_rf}/turmas/anos_letivos/{ano_letivo}/"
    )
    turmas = _client.json_or_none(resp)
    if not isinstance(turmas, list):
        return []

    saida: list[dict[str, Any]] = []

    for turma in turmas:
        saida.append(_montar_turma_atribuida_professor(turma))

    return saida


def verificar_atribuicao_professor_turma(
    codigo_rf: str, codigo_turma: str, data: str
) -> bool:
    """Verifica se o professor tem atribuição na turma.

    Args:
        codigo_rf: RF usado na consulta.
        codigo_turma: Código da turma usada na consulta.
        data: Data usada na consulta.

    Returns:
        ``True`` quando o professor tem atribuição na turma.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_rf}/turmas/{codigo_turma}/"
        f"atribuicao/verificar/data/?data_consulta={data}"
    )
    return bool(_client.json_or_none(resp))


def get_status_atribuicao_professor_turma(
    codigo_rf: str, codigo_turma: str
) -> dict[str, Any] | None:
    """Retorna o status da atribuição do professor na turma.

    Args:
        codigo_rf: RF usado na consulta.
        codigo_turma: Código da turma usada na consulta.

    Returns:
        Status da atribuição ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_rf}/turmas/{codigo_turma}/atribuicao/status/"
    )
    payload = _client.json_or_none(resp)
    if payload is None:
        return None

    return cast(dict[str, Any], payload)


def verificar_atribuicao_professor_turma_disciplina(
    codigo_rf: str,
    codigo_turma: str,
    disciplina_id: str,
    data: int | str,
) -> bool:
    """Verifica se o professor tem atribuição na turma e disciplina.

    Args:
        codigo_rf: RF usado na consulta.
        codigo_turma: Código da turma usada na consulta.
        disciplina_id: ID da disciplina usada na consulta.
        data : Data tick usada na consulta.

    Returns:
        ``True`` quando o professor tem atribuição na turma e disciplina.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_rf}/turmas/{codigo_turma}/disciplinas/{disciplina_id}/atribuicao/verificar/datatick/?data_consulta_tick={data}"
    )

    return bool(_client.json_or_none(resp))


def verificar_recorrencia_datas(
    codigo_rf: str,
    codigo_turma: str,
    disciplina_id: str,
    datas_ticks: list[str],
    atribuicoes_rf: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Verifica datas recorrentes de uma atribuição docente.

    Args:
        codigo_rf: RF usado na consulta.
        codigo_turma: Código da turma usada na consulta.
        disciplina_id: ID da disciplina usada na consulta.
        datas_ticks: Datas recorrentes em ticks de DateTime do .NET.
        atribuicoes_rf: Atribuições previamente preparadas.

    Returns:
        Permissões de persistência por data.

    Raises:
        httpx.HTTPError: Quando uma das chamadas aos sidecars falha.
        ValueError: Quando um tick informado é inválido.
    """
    data_tick_padrao = datas_ticks[0] if datas_ticks else None
    if not data_tick_padrao:
        return []

    ano_letivo = obter_ano_tick(data_tick_padrao)

    if atribuicoes_rf is None:
        atribuicoes_rf = _get_atribuicoes_professor_turma_disciplina(
            codigo_rf, disciplina_id, ano_letivo
        )

    componentes_api_eol = pedagogico_services.get_componentes_api_eol()
    ids_componentes_filhos = {
        str(componente.get("id_componente_curricular"))
        for componente in componentes_api_eol
        if str(componente.get("id_componente_curricular_pai")) == disciplina_id
    }

    retorno: list[dict[str, Any]] = []
    for data_tick in datas_ticks:
        data_consulta = datetime_de_tick(data_tick)
        pode_persistir = any(
            _atribuicao_permite_persistir(
                atribuicao,
                codigo_turma,
                disciplina_id,
                ids_componentes_filhos,
                data_consulta,
            )
            for atribuicao in atribuicoes_rf
            if isinstance(atribuicao, dict)
        )
        retorno.append(
            {
                "data": data_consulta.isoformat(),
                "pode_persistir": pode_persistir,
            }
        )

    return retorno


def verificar_atribuicao_periodo(
    codigo_rf: str,
    codigo_turma: str,
    disciplina_id: str,
    data_inicio: str,
    data_fim: str,
    atribuicoes_rf: list[dict[str, Any]] | None = None,
) -> bool:
    """Verifica se o professor tem atribuição na turma e disciplina no período.

    Args:
        codigo_rf: RF usado na consulta.
        codigo_turma: Código da turma usada na consulta.
        disciplina_id: ID da disciplina usada na consulta.
        data_inicio: Data de início do período.
        data_fim: Data de fim do período.
        atribuicoes_rf: Atribuições previamente preparadas.

    Returns:
        ``True`` quando o professor tem atribuição na turma e disciplina
          no período.
    """
    data_inicio_periodo = _parse_datetime_atribuicao(data_inicio)
    data_fim_periodo = _parse_datetime_atribuicao(data_fim)
    if (
        data_inicio_periodo is None
        or data_fim_periodo is None
        or data_inicio_periodo > data_fim_periodo
    ):
        return False

    if atribuicoes_rf is None:
        atribuicoes_rf = _get_atribuicoes_professor_turma_disciplina(
            codigo_rf,
            disciplina_id,
            0,
        )
    componentes_api_eol = pedagogico_services.get_componentes_api_eol()
    ids_componentes_filhos = {
        str(componente.get("id_componente_curricular"))
        for componente in componentes_api_eol
        if str(componente.get("id_componente_curricular_pai")) == disciplina_id
    }

    return any(
        _atribuicao_sobrepoe_periodo(
            atribuicao,
            codigo_turma,
            disciplina_id,
            ids_componentes_filhos,
            data_inicio_periodo,
            data_fim_periodo,
        )
        for atribuicao in atribuicoes_rf
    )


def _atribuicao_sobrepoe_periodo(
    atribuicao: dict[str, Any],
    codigo_turma: str,
    disciplina_id: str,
    ids_componentes_filhos: set[str],
    data_inicio_periodo: datetime,
    data_fim_periodo: datetime,
) -> bool:
    """Verifica se uma atribuição corresponde e sobrepõe um período.

    Args:
        atribuicao: Dados normalizados da atribuição do professor.
        codigo_turma: Código da turma consultada.
        disciplina_id: ID da disciplina consultada.
        ids_componentes_filhos: IDs dos componentes filhos da disciplina.
        data_inicio_periodo: Início do período consultado.
        data_fim_periodo: Fim do período consultado.

    Returns:
        ``True`` quando turma e disciplina correspondem e os períodos se
        sobrepõem.
    """
    data_inicio_atribuicao = _parse_datetime_atribuicao(
        atribuicao.get("data_inicio_atribuicao")
    )
    data_fim_atribuicao = _parse_datetime_atribuicao(
        atribuicao.get("data_fim_atribuicao")
    )
    if data_inicio_atribuicao is None or data_fim_atribuicao is None:
        return False

    disciplina_atribuicao = str(atribuicao.get("disciplina_id"))
    turma_e_disciplina_correspondem = str(
        atribuicao.get("codigo_turma")
    ) == codigo_turma and (
        disciplina_atribuicao == disciplina_id
        or disciplina_atribuicao in ids_componentes_filhos
    )
    periodo_sobreposto = (
        data_inicio_atribuicao <= data_inicio_periodo <= data_fim_atribuicao
        or data_inicio_atribuicao <= data_fim_periodo <= data_fim_atribuicao
        or data_inicio_periodo
        <= data_inicio_atribuicao
        <= data_fim_atribuicao
        <= data_fim_periodo
    )
    return turma_e_disciplina_correspondem and periodo_sobreposto


def _get_atribuicoes_professor_turma_disciplina(
    codigo_rf: str, disciplina_id: str, ano_letivo: int
) -> list[dict[str, Any]]:
    """Retorna atribuições do professor na disciplina no ano letivo.

    Args:
        codigo_rf: RF usado na consulta.
        disciplina_id: ID da disciplina usada na consulta.
        ano_letivo: Ano letivo de referência.

    Returns:
        Lista de atribuições ou ausência de conteúdo.
    """
    if _validar_componente_eh_territorio_saber_agrupado(disciplina_id):
        if ano_letivo > 0:
            payload = pedagogico_services.get_atribuicoes_territorio_saber(
                codigo_rf,
                ano_letivo,
            )
        else:
            payload = pedagogico_services.get_atribuicoes_territorio_saber(
                codigo_rf
            )
    else:
        if ano_letivo > 0:
            resp = _client.get(
                f"{_BASE}/{codigo_rf}/turmas/anos_letivos/{ano_letivo}/"
            )
        else:
            resp = _client.get(f"{_BASE}/{codigo_rf}/turmas/anos_letivos/")
        payload = _client.json_or_none(resp)

    if not isinstance(payload, list):
        return []

    return [item for item in payload if isinstance(item, dict)]


def get_atribuicoes_professor_turma_disciplina(
    codigo_rf: str,
    disciplina_id: str,
    ano_letivo: int,
) -> list[dict[str, Any]]:
    """Retorna atribuições do professor na disciplina no ano letivo.

    Args:
        codigo_rf: RF usado na consulta.
        disciplina_id: ID da disciplina usada na consulta.
        ano_letivo: Ano letivo de referência.

    Returns:
        Lista de atribuições ou ausência de conteúdo.
    """
    return _get_atribuicoes_professor_turma_disciplina(
        codigo_rf,
        disciplina_id,
        ano_letivo,
    )


def _parse_datetime_atribuicao(valor: Any) -> datetime | None:
    """Converta uma data de atribuição para comparação interna."""
    if isinstance(valor, datetime):
        return valor.replace(tzinfo=None)
    if isinstance(valor, date):
        return datetime.combine(valor, datetime.min.time())
    if not isinstance(valor, str) or not valor.strip():
        return None
    try:
        return datetime.fromisoformat(
            valor.strip().replace("Z", "+00:00")
        ).replace(tzinfo=None)
    except ValueError:
        return None


def _atribuicao_permite_persistir(
    atribuicao: dict[str, Any],
    codigo_turma: str,
    disciplina_id: str,
    ids_componentes_filhos: set[str],
    data_consulta: datetime,
) -> bool:
    """Aplique a regra legada de persistência para uma atribuição.

    Args:
        atribuicao: Dados da atribuição do professor.
        codigo_turma: Código da turma consultada.
        disciplina_id: ID da disciplina consultada.
        ids_componentes_filhos: IDs dos componentes filhos da disciplina.
        data_consulta: Data de recorrência que será verificada.

    Returns:
        ``True`` quando a atribuição permite persistir na data consultada.
    """
    data_inicio = _parse_datetime_atribuicao(
        atribuicao.get("data_inicio_atribuicao")
    )
    data_fim = _parse_datetime_atribuicao(
        atribuicao.get("data_fim_atribuicao")
    )
    data_fim_turma = _parse_datetime_atribuicao(
        atribuicao.get("data_fim_turma")
    )
    disciplina_atribuicao = str(atribuicao.get("disciplina_id"))

    atribuicao_na_data = (
        str(atribuicao.get("codigo_turma")) == codigo_turma
        and (
            disciplina_atribuicao == disciplina_id
            or disciplina_atribuicao in ids_componentes_filhos
        )
        and data_inicio is not None
        and data_fim is not None
        and data_inicio <= data_consulta <= data_fim
    )
    atribuicao_ate_fim_turma = (
        data_fim is not None
        and data_fim_turma is not None
        and data_fim >= data_fim_turma
    )
    return atribuicao_na_data or atribuicao_ate_fim_turma


def verificar_atribuicao_disciplina_territorio_saber(
    codigo_rf: str,
    codigo_turma: str,
    disciplina_id: str,
    data: str,
    territorio_saber: bool = False,
) -> bool:
    """Verifica atribuição na disciplina e território do saber.

    Args:
        codigo_rf: RF usado na consulta.
        codigo_turma: Código da turma usada na consulta.
        disciplina_id: ID da disciplina usada na consulta.
        data: Data usada na consulta.
        territorio_saber: Indica se a verificação é para território do saber.

    Returns:
        ``True`` quando o professor tem atribuição na disciplina e
        território do saber.
    """
    if territorio_saber:
        return pedagogico_services.verificar_atriuicao_territorio_saber(
            codigo_rf, codigo_turma, disciplina_id, data
        )

    resp = _client.get(
        f"{_BASE}/{codigo_rf}/turmas/{codigo_turma}/disciplinas/{disciplina_id}/atribuicao/verificar/data/?data_consulta={data}"
    )

    return bool(_client.json_or_none(resp))


def get_atribuicoes_turma_disciplina(
    codigo_turma: str, disciplina_id: str, data: str
) -> list[dict[str, Any]]:
    """Retorna as atribuições de uma turma e disciplina.

    Args:
        codigo_turma: Código da turma usada na consulta.
        disciplina_id: ID da disciplina usada na consulta.
        data: Data tick usada na consulta.

    Returns:
        Lista de atribuições ou ausência de conteúdo.
    """
    resp = _client.get(
        f"{_BASE}/{codigo_turma}/disciplinas/{disciplina_id}/"
        "atribuicao/data/",
        params={"data_ticks": data},
    )
    payload = _client.json_or_none(resp)
    if not isinstance(payload, list):
        return []

    return payload


def _montar_turma_atribuida_professor_escola(
    turma: dict[str, Any],
) -> dict[str, Any]:
    """Monta uma linha de turma atribuída simplificada a partir da turma.

    Args:
        turma: Dados da turma no recorte de etapa.

    Returns:
        Dicionário em snake_case pronto para serialização.
    """
    return {
        "codigoTurma": turma.get("codigo_turma"),
        "nomeTurma": turma.get("nome_turma"),
        "componenteCurricular": turma.get("componente_curricular"),
        "dataInicioAtribuicao": turma.get("data_inicio_turma"),
        "dataFimAtribuicao": turma.get("data_fim_atribuicao"),
        "ano": turma.get("ano"),
        "etapaEnsino": turma.get("etapa_ensino"),
    }


def _montar_turma_atribuida_professor(
    turma: dict[str, Any],
) -> dict[str, Any]:
    """Monta uma linha de turma atribuída simplificada a partir da turma.

    Args:
        turma: Dados da turma no recorte de etapa.

    Returns:
        Dicionário em snake_case pronto para serialização.
    """
    return {
        "codigoTurma": turma.get("codigo_turma"),
        "nomeTurma": turma.get("nome_turma"),
        "componenteCurricular": turma.get("componente_curricular"),
        "dataInicioAtribuicao": turma.get("data_inicio_turma"),
        "dataFimAtribuicao": turma.get("data_disponibilizacao"),
        "ano": turma.get("ano"),
        "etapaEnsino": turma.get("etapa_ensino"),
    }


def get_administradores_sgp_escola(codigo_ue: str) -> list[str]:
    """Retorna lista de RFs dos administradores SGP da escola.

    Args:
        codigo_ue: Código EOL da unidade educacional.

    Returns:
        Lista de RFs/logins dos administradores SGP (ADM UE e ADM DRE).
        Retorna lista vazia se não houver administradores ou em caso de erro.
    """
    resp = _client.get(f"{_BASE_ESCOLAS}/{codigo_ue}/administrador-sgp")
    data = _client.json_or_none(resp)
    if not isinstance(data, list):
        return []
    return [str(rf) for rf in data if rf]


def _validar_componente_eh_territorio_saber_agrupado(
    codigo_componente: str,
) -> bool:
    """Valida se o componente curricular é agrupado em Território do Saber.

    Args:
        codigo_componente: Código do componente curricular.

    Returns:
        True se o componente é agrupado; False caso contrário.
    """
    try:
        return (
            int(codigo_componente)
            >= _COMPONENTE_AGRUPAMENTO_TERRITORIO_SABER_ID_INICIAL
        )
    except (TypeError, ValueError):
        return False


def _verificar_vigencia_componente_pai(
    componentes_api_eol: list[dict[str, Any]],
    disciplina_id: str,
    data_referencia: datetime | None,
) -> bool:
    """Verifica se o componente curricular pai está vigente.

    Args:
        componentes_api_eol: Lista de componentes curriculares do EOL.
        disciplina_id: ID da disciplina usada na consulta.
        data_referencia: Data de referência para verificar a vigência. Na
            ausência, utiliza a data atual.

    Returns:
        True se o componente curricular pai estiver vigente; False
        caso contrário.
    """
    componente = next(
        (
            item
            for item in componentes_api_eol
            if isinstance(item, dict)
            and str(item.get("id_componente_curricular")) == disciplina_id
        ),
        None,
    )
    if componente is None:
        return False

    codigo_componente_pai = componente.get("id_componente_curricular_pai")
    if codigo_componente_pai is None:
        return False

    data_base = _parse_datetime_atribuicao(data_referencia)
    if data_base is None:
        data_base = datetime.combine(date.today(), datetime.min.time())

    for item in componentes_api_eol:
        if not isinstance(item, dict) or str(
            item.get("id_componente_curricular")
        ) != str(codigo_componente_pai):
            continue

        vigencia = item.get("vigencia")
        if vigencia is None:
            return True
        data_vigencia = _parse_datetime_atribuicao(vigencia)
        return data_vigencia is not None and data_vigencia >= data_base

    return False


def buscar_professores_titulares_por_turmas(
    codigos_turmas: list[str],
) -> list[dict[str, Any]]:
    """Busca professores titulares de uma lista de turmas.

    Args:
        codigos_turmas: Lista de códigos das turmas consultadas.

    Returns:
        Professores titulares encontrados ou uma lista vazia.

    Raises:
        httpx.HTTPError: Quando a chamada ao serviço de professores falha.
        ValueError: Quando a resposta não pode ser convertida para JSON.
    """
    resp = _client.get(
        f"{_BASE}/titulares/",
        params={"codigos_turmas": [int(codigo) for codigo in codigos_turmas]},
    )
    payload = _client.json_or_none(resp)
    if not isinstance(payload, list):
        return []

    atribuicoes_professores = [
        item for item in payload if isinstance(item, dict)
    ]

    componentes_api_eol = pedagogico_services.get_componentes_api_eol()

    atribuicoes_territorio_saber = (
        pedagogico_services.get_professores_turmas_territorio_saber(
            codigos_turmas
        )
    )

    if isinstance(atribuicoes_territorio_saber, list) and any(
        atribuicoes_territorio_saber
    ):
        atribuicoes_professores = _tratar_agrupamento_componentes_professor(
            codigos_turmas,
            atribuicoes_professores,
            atribuicoes_territorio_saber,
        )

    componentes_retorno: list[dict[str, Any]] = []
    for codigo_turma in codigos_turmas:
        componentes_turma = [
            _montar_componente_professor_agrupado(
                componente,
                componentes_api_eol,
            )
            for componente in atribuicoes_professores
            if str(componente.get("turma_id")) == codigo_turma
        ]
        _aplicar_descricoes_componentes_turma(
            codigo_turma,
            componentes_turma,
        )
        componentes_retorno.extend(componentes_turma)

    return _agrupar_componentes_retorno(componentes_retorno)
