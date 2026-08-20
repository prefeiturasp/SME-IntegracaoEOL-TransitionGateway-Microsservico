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
    "apps.abrangencia",
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

PEDAGOGICO_API_URL = os.getenv("PEDAGOGICO_API_URL", "http://localhost:9004")
PEDAGOGICO_API_KEY = os.getenv("PEDAGOGICO_API_KEY", "")
PEDAGOGICO_API_KEY_HEADER = os.getenv("PEDAGOGICO_API_KEY_HEADER", "X-API-Key")

PROFESSORES_API_URL = os.getenv("PROFESSORES_API_URL", "http://localhost:9005")
PROFESSORES_API_KEY = os.getenv("PROFESSORES_API_KEY", "")
PROFESSORES_API_KEY_HEADER = os.getenv(
    "PROFESSORES_API_KEY_HEADER", "X-API-Key"
)

INSTITUCIONAL_API_URL = os.getenv(
    "INSTITUCIONAL_API_URL", "http://localhost:9006"
)
INSTITUCIONAL_API_KEY = os.getenv("INSTITUCIONAL_API_KEY", "")
INSTITUCIONAL_API_KEY_HEADER = os.getenv(
    "INSTITUCIONAL_API_KEY_HEADER", "X-API-Key"
)

PROGRAMASEDU_API_URL = os.getenv(
    "PROGRAMASEDU_API_URL", "http://localhost:9006"
)
PROGRAMASEDU_API_KEY = os.getenv("PROGRAMASEDU_API_KEY", "")
PROGRAMASEDU_API_KEY_HEADER = os.getenv(
    "PROGRAMASEDU_API_KEY_HEADER", "X-API-Key"
)

ALUNOS_API_URL = os.getenv("ALUNOS_API_URL", "http://localhost:9007")
ALUNOS_API_KEY = os.getenv("ALUNOS_API_KEY", "")
ALUNOS_API_KEY_HEADER = os.getenv("ALUNOS_API_KEY_HEADER", "X-API-Key")
