"""Configuração Django do TransitionGateway."""

import os
from pathlib import Path

from apps.alunos.utils import aluno_turmas_operation

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "apps.core.apps.CoreConfig",
    "apps.pedagogico",
    "apps.professores",
    "apps.programasedu",
    "apps.institucional",
    "apps.alunos",
    "apps.matriculas",
]

MIDDLEWARE = [
    "sme_sidecar_sdk.integrations.django.ObservabilityMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

API_KEY = os.getenv("API_KEY", "dev-key-default")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "config.authentication.ApiKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SME - API/EOL",
    "DESCRIPTION": "Porta de entrada única para os domínios internos.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # Mantém os parâmetros na ordem declarada nas views, alinhada ao Swagger
    # do legado, em vez da ordenação alfabética padrão.
    "SORT_OPERATION_PARAMETERS": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": API_KEY_HEADER,
            }
        }
    },
    "APPEND_PATHS": {
        "/api/v1/alunos/{codigo_aluno}/turmas": aluno_turmas_operation(
            "v1_alunos_turmas_list"
        ),
    },
    "SECURITY": [{"ApiKeyAuth": []}],
    "SWAGGER_UI_SETTINGS": {
        "syntaxHighlight": False,
    },
}

SIDECAR_PEDAGOGICO_URL = os.getenv(
    "SIDECAR_PEDAGOGICO_URL", "http://localhost:9004"
)
SIDECAR_PEDAGOGICO_API_KEY = os.getenv("SIDECAR_PEDAGOGICO_API_KEY", "")
SIDECAR_PEDAGOGICO_API_KEY_HEADER = os.getenv(
    "SIDECAR_PEDAGOGICO_API_KEY_HEADER", "X-API-Key"
)

SIDECAR_PROFESSORES_URL = os.getenv(
    "SIDECAR_PROFESSORES_URL", "http://localhost:9005"
)
SIDECAR_PROFESSORES_API_KEY = os.getenv("SIDECAR_PROFESSORES_API_KEY", "")
SIDECAR_PROFESSORES_API_KEY_HEADER = os.getenv(
    "SIDECAR_PROFESSORES_API_KEY_HEADER", "X-API-Key"
)

SIDECAR_INSTITUCIONAL_URL = os.getenv(
    "SIDECAR_INSTITUCIONAL_URL", "http://localhost:9006"
)
SIDECAR_INSTITUCIONAL_API_KEY = os.getenv("SIDECAR_INSTITUCIONAL_API_KEY", "")
SIDECAR_INSTITUCIONAL_API_KEY_HEADER = os.getenv(
    "SIDECAR_INSTITUCIONAL_API_KEY_HEADER", "X-API-Key"
)

SIDECAR_PROGRAMASEDU_URL = os.getenv(
    "SIDECAR_PROGRAMASEDU_URL", "http://localhost:9006"
)
SIDECAR_PROGRAMASEDU_API_KEY = os.getenv("SIDECAR_PROGRAMASEDU_API_KEY", "")
SIDECAR_PROGRAMASEDU_API_KEY_HEADER = os.getenv(
    "SIDECAR_PROGRAMASEDU_API_KEY_HEADER", "X-API-Key"
)

SIDECAR_ALUNOS_URL = os.getenv("SIDECAR_ALUNOS_URL", "http://localhost:9007")
SIDECAR_ALUNOS_API_KEY = os.getenv("SIDECAR_ALUNOS_API_KEY", "")
SIDECAR_ALUNOS_API_KEY_HEADER = os.getenv(
    "SIDECAR_ALUNOS_API_KEY_HEADER", "X-API-Key"
)
