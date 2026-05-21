"""Serviços de integração do domínio professores."""

from typing import Any

from django.conf import settings

from apps.core.http_client import ServiceClient

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


def get_professor(rf_professor: str) -> Any:
    """Retorna o nome do professor.

    Args:
        rf_professor: Registro funcional usado na consulta.

    Returns:
        Nome extraído do payload, texto bruto ou ausência de conteúdo.
    """
    resp = _client.get(f"{_BASE}/{rf_professor}")
    data = _client.json_or_none(resp)
    if isinstance(data, dict):
        return data.get("nome")
    return data


def get_validade_professor(codigo_rf: str) -> Any:
    """Verifica se o professor está válido para uso."""
    resp = _client.get(f"{_BASE}/{codigo_rf}/validade")
    return resp.json()


def get_funcionario_ativo(registro_funcional: str) -> Any:
    """Verifica se o funcionário está ativo."""
    resp = _client.get(
        f"{_BASE_ACESSOS}/funcionario-ativo/{registro_funcional}"
    )
    return resp.json()


def get_nome_servidor(registro_funcional: str) -> Any:
    """Retorna dados de identificação do servidor."""
    resp = _client.get(
        f"{_BASE_FUNCIONARIOS}/nome-servidor/{registro_funcional}"
    )
    return _client.json_or_none(resp)


def get_nome_usuario_eol(registro_funcional: str) -> Any:
    """Retorna nome de usuário EOL do funcionário."""
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
        codigos_rf: RFs enviados ao sidecar.

    Returns:
        Lista de professores ou ausência de conteúdo.
    """
    resp = _client.post(
        f"{_BASE_FUNCIONARIOS}/BuscarPorListaRF/",
        payload=codigos_rf,
    )
    return _client.json_or_none(resp)


def get_funcionarios_escola(codigo_ue: str) -> Any:
    """Retorna funcionários vinculados à escola."""
    resp = _client.get(f"{_BASE_ESCOLAS}/{codigo_ue}/funcionarios")
    return _client.json_or_none(resp)


def get_funcionarios_escola_por_cargo(
    codigo_ue: str,
    codigo_cargo: str,
) -> Any:
    """Retorna funcionários da escola filtrados por cargo."""
    resp = _client.get(
        f"{_BASE_ESCOLAS}/{codigo_ue}/funcionarios/cargos/{codigo_cargo}"
    )
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
        f"{_BASE}/{codigo_rf}/disciplina/{disciplina_id}/turmas",
        payload=codigos_turma,
    )
    return _client.json_or_none(resp)
