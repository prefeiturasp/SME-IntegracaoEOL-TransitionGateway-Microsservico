"""Serviços do domínio de abrangência (estrutura institucional vigente)."""

from typing import Any

from apps.core.api_clients import get_api_client
from apps.core.datetime import formatar_datetime_legado

_BASE_TURMAS = "/api/v1/pedagogico/turmas"

_client = get_api_client("pedagogico")


def _formatar_datas_turma(turma: dict[str, Any]) -> dict[str, Any]:
    """Formata as datas de uma turma no padrão ISO.

    Args:
        turma: Turma no contrato de abrangência (camelCase), como devolvida
            pelo sidecar Pedagógico.

    Returns:
        A mesma turma com ``dataFim``/``dataInicioTurma`` reformatadas.
    """
    return {
        **turma,
        "dataFim": formatar_datetime_legado(turma.get("dataFim")),
        "dataInicioTurma": formatar_datetime_legado(
            turma.get("dataInicioTurma")
        ),
    }


def _estrutura_legado(payload: Any) -> dict[str, Any]:
    """Normaliza a estrutura de abrangência para o contrato.

    O sidecar Pedagógico devolve ``{"abrangencia": None, "dres": [...]}`` —
    o campo ``abrangencia`` não existe em ``EstruturaInstitucionalDTO`` e
    não deve ser repassado ao cliente do gateway.

    Args:
        payload: Corpo retornado pelo sidecar Pedagógico.

    Returns:
        Estrutura ``{"dres": [...]}`` no contrato, com as datas de
        cada turma já formatadas.
    """
    dres = payload.get("dres", []) if isinstance(payload, dict) else []
    return {
        "dres": [
            {
                **dre,
                "ues": [
                    {
                        **ue,
                        "turmas": [
                            _formatar_datas_turma(turma)
                            for turma in ue.get("turmas", [])
                        ],
                    }
                    for ue in dre.get("ues", [])
                ],
            }
            for dre in dres
        ]
    }


def get_estrutura_vigente_por_dre(codigo_dre: str) -> dict[str, Any]:
    """Retorna a estrutura institucional vigente de uma DRE.

    Args:
        codigo_dre: Código EOL da DRE.

    Returns:
        Estrutura ``{"dres": [...]}`` no contrato; ``dres`` vazio
        quando a DRE não tem turmas no recorte de tipo de escola.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
    """
    resp = _client.get(
        f"{_BASE_TURMAS}/turmas-atribuidas-dre-ue/todas/",
        params={"codigo_dre": codigo_dre},
    )
    resp.raise_for_status()
    return _estrutura_legado(_client.json_or_none(resp))


def get_estrutura_vigente_por_turmas(
    codigos_turma: list[int],
) -> dict[str, Any]:
    """Retorna a estrutura institucional vigente de uma lista de turmas.

    Args:
        codigos_turma: Códigos das turmas a consultar.

    Returns:
        Estrutura ``{"dres": [...]}`` no contrato; ``dres`` vazio
        quando a lista é vazia ou nenhuma turma está no recorte.

    Raises:
        httpx.HTTPError: Se a chamada ao serviço pedagógico falhar.
    """
    if not codigos_turma:
        return {"dres": []}
    resp = _client.post(
        f"{_BASE_TURMAS}/turmas-atribuidas-dre-ue/por-turmas/",
        payload=codigos_turma,
    )
    resp.raise_for_status()
    return _estrutura_legado(_client.json_or_none(resp))
