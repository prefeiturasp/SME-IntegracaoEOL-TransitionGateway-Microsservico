"""Serviços de integração do domínio professores."""

from typing import Any

from django.conf import settings

from apps.core.datetime import datetime_legado
from apps.core.http_client import ServiceClient
from apps.institucional import services as institucional_services
from apps.pedagogico import services as pedagogico_services
from apps.professores.serializers import (
    AbrangenciaLegadoSerializer,
    DisciplinaTurmaAgrupamentoSerializer,
    DisciplinaTurmaAtribuidaSerializer,
    FuncionarioLegadoSerializer,
    ProfessorAtribuicaoTurmaDisciplinaSerializer,
    ProfessorStatusAtribuicaoSerializer,
    TurmaElegivelLegadoSerializer,
    TurmasAtribuidasLegadoSerializer,
)

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

_client = ServiceClient(
    base_url=settings.PROFESSORES_API_URL,
    dominio="professores",
    api_key=settings.PROFESSORES_API_KEY,
    api_key_header=settings.PROFESSORES_API_KEY_HEADER,
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
        Disciplinas no contrato legado.
    """
    data = pedagogico_services.get_componentes_por_lista_turmas(
        [codigo_turma],
        adicionar_componentes_planejamento=False,
        incluir_extintas=True,
    )
    if not isinstance(data, list):
        return data
    return DisciplinaTurmaAgrupamentoSerializer(data, many=True).data


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
        Disciplinas no contrato legado.
    """
    data = _get_componentes_por_switch(
        login=login,
        id_perfil=id_perfil,
        codigo_turma=codigo_turma,
        planejamento=planejamento,
        abrangencia=abrangencia,
        cargos=cargos,
    )
    if not isinstance(data, list):
        return data
    return DisciplinaTurmaAtribuidaSerializer(data, many=True).data


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
        data = TurmasAtribuidasLegadoSerializer(
            montar_turmas_atribuidas_professor(login)
        ).data
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
        if isinstance(data, dict):
            data = AbrangenciaLegadoSerializer(data).data

    if isinstance(data, dict):
        data["abrangencia"] = _bloco_abrangencia_temporario(
            id_perfil, abrangencia, cargos, funcoes, grupo, eh_perfil_manual
        )
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
        Abrangência de turmas no contrato legado.
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
    if not isinstance(data, list):
        return data
    return TurmasAtribuidasLegadoSerializer(data).data


def get_abrangencia_ues(codigos_ue: list[str]) -> Any:
    """Retorna abrangência de turmas para unidades.

    Args:
        codigos_ue: Códigos EOL das unidades educacionais.

    Returns:
        Abrangência de turmas ou ausência de conteúdo.
    """
    data = pedagogico_services.get_turmas_atribuidas_dre_ue(codigos_ue)
    return TurmasAtribuidasLegadoSerializer(data).data


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
    if not isinstance(data, list):
        return data
    return TurmaElegivelLegadoSerializer(data, many=True).data


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
    if not isinstance(data, list):
        return data
    return FuncionarioLegadoSerializer(data, many=True).data


def _bloco_abrangencia_temporario(
    id_perfil: str,
    abrangencia: int | None,
    cargos: list[int] | None,
    funcoes: list[int] | None,
    grupo: int | None,
    eh_perfil_manual: bool,
) -> dict[str, Any] | None:
    """Monta o bloco de abrangência a partir dos parâmetros temporários.

    Os valores viriam da identidade (CoreSSO); enquanto a integração não
    existe, são informados por parâmetros temporários de consulta.
    """
    if not any(
        valor is not None for valor in (abrangencia, cargos, funcoes, grupo)
    ):
        return None
    return {
        "grupoID": id_perfil,
        "cargosId": cargos or [],
        "funcoesId": funcoes or [],
        "grupo": grupo,
        "abrangencia": abrangencia,
        "ehPerfilManual": eh_perfil_manual,
    }


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
        f"{_BASE}/{codigo_rf}/turmas/{codigo_turma}/verificar-atribuicao/?data_consulta={data}"
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

    serializer = ProfessorStatusAtribuicaoSerializer(payload)
    return dict(serializer.data)


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

    serializer = ProfessorAtribuicaoTurmaDisciplinaSerializer(
        payload,
        many=True,
    )
    return [dict(item) for item in serializer.data]


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
