"""Utilitários do app de alunos."""


def aluno_turmas_legacy_parameters() -> list[dict]:
    """Monta os parâmetros legados do endpoint de turmas do aluno.

    Returns:
        Lista de parâmetros OpenAPI no mesmo formato exposto pelo legado.
    """
    return [
        {
            "in": "path",
            "name": "codigo_aluno",
            "schema": {"type": "integer", "format": "int32"},
            "required": True,
        },
        {
            "in": "path",
            "name": "ano_letivo",
            "schema": {"type": "integer", "format": "int32"},
            "required": True,
        },
        {
            "in": "path",
            "name": "historico",
            "schema": {"type": "boolean"},
            "required": True,
        },
        {
            "in": "path",
            "name": "filtrar_situacao",
            "schema": {"type": "boolean", "default": True},
            "required": True,
        },
        {
            "in": "path",
            "name": "tipo_turma",
            "schema": {"type": "boolean", "default": True},
            "required": True,
        },
    ]


def aluno_turmas_legacy_operation(operation_id: str) -> dict:
    """Monta a operação OpenAPI legada para turmas do aluno.

    Args:
        operation_id: Identificador único da operação no schema OpenAPI.

    Returns:
        Dicionário OpenAPI usado em ``SPECTACULAR_SETTINGS.APPEND_PATHS``.
    """
    return {
        "get": {
            "operationId": operation_id,
            "tags": ["Alunos"],
            "summary": "Turmas do aluno",
            "description": "Retorna lista de turmas do aluno.",
            "parameters": aluno_turmas_legacy_parameters(),
            "responses": {"200": {"description": "Success"}},
            "security": [{"ApiKeyAuth": []}],
        }
    }
