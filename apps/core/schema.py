"""Hooks de pós-processamento do schema OpenAPI."""

from typing import Any


def converter_examples_de_path_em_default(
    result: dict[str, Any],
    generator: Any,
    request: Any,
    public: bool,
) -> dict[str, Any]:
    """Move o valor de exemplo dos parâmetros de path para ``default``.

    A especificação OpenAPI proíbe ``default`` em parâmetro obrigatório e o
    drf-spectacular o descarta em parâmetros de path. O Swagger do legado
    (Swashbuckle) emite o default mesmo assim e a UI o exibe como
    "Default value" pré-preenchido, sem o seletor de "Examples". Este hook
    replica esse comportamento: move o valor do primeiro exemplo declarado
    para ``schema.default`` e remove o bloco de exemplos.
    """
    for path_item in result.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            for parametro in operation.get("parameters", []):
                if parametro.get("in") != "path":
                    continue
                exemplos = parametro.get("examples")
                if not exemplos:
                    continue
                primeiro = next(iter(exemplos.values()))
                parametro.setdefault("schema", {})["default"] = primeiro.get(
                    "value"
                )
                del parametro["examples"]
    return result
