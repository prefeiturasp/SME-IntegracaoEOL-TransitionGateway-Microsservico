"""Utilitários do app de alunos."""


def aluno_turmas_operation(operation_id: str) -> dict:
    """Monta a operação OpenAPI para turmas do aluno.

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
            "parameters": [
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
            ],
            "responses": {"200": {"description": "Success"}},
            "security": [{"ApiKeyAuth": []}],
        }
    }
