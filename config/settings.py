"""Configurações Django do SME-IntegracaoEOL-TransitionGateway-Microsservico."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("DJANGO_DEBUG", "1") == "0":
        raise ImproperlyConfigured(
            "A variável DJANGO_SECRET_KEY é obrigatória em produção."
        )
    SECRET_KEY = os.getenv("HOSTNAME", "dev-secret-key")

DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")
]

INSTALLED_APPS = [
    "elasticapm.contrib.django",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "apps.core",
    "apps.controle_gateway",
    "apps.institucional",
    "apps.professores",
    "apps.alunos",
    "apps.pedagogico",
    "apps.programas",
]

MIDDLEWARE = [
    "elasticapm.contrib.django.middleware.TracingMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ── Identidade da aplicação ───────────────────────────────────────────────────
NOME_APLICACAO = os.getenv(
    "NOME_APLICACAO", "SME-IntegracaoEOL-TransitionGateway-Microsservico"
)
AMBIENTE_APLICACAO = os.getenv("AMBIENTE_APLICACAO", "local")
NIVEL_LOG = os.getenv("NIVEL_LOG", "INFO")
LOG_ENVIRONMENT = os.getenv("LOG_ENVIRONMENT", AMBIENTE_APLICACAO)

# ── Autenticação da API ───────────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY", "dev-key-default")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")

# ── URLs dos sidecars por domínio ─────────────────────────────────────────────
SIDECAR_INSTITUCIONAL_URL = os.getenv(
    "SIDECAR_INSTITUCIONAL_URL", "http://localhost:9001"
)
SIDECAR_PROFESSORES_URL = os.getenv(
    "SIDECAR_PROFESSORES_URL", "http://localhost:9002"
)
SIDECAR_ALUNOS_URL = os.getenv("SIDECAR_ALUNOS_URL", "http://localhost:9003")
SIDECAR_PEDAGOGICO_URL = os.getenv(
    "SIDECAR_PEDAGOGICO_URL", "http://localhost:9004"
)
SIDECAR_PROGRAMAS_URL = os.getenv(
    "SIDECAR_PROGRAMAS_URL", "http://localhost:9005"
)

# ── Configurações do gateway (resiliência) ────────────────────────────────────
GATEWAY_CIRCUIT_BREAKER_FAIL_MAX = int(
    os.getenv("GATEWAY_CIRCUIT_BREAKER_FAIL_MAX", "5")
)
GATEWAY_CIRCUIT_BREAKER_RESET_TIMEOUT = int(
    os.getenv("GATEWAY_CIRCUIT_BREAKER_RESET_TIMEOUT", "30")
)
GATEWAY_RETRY_MAX_ATTEMPTS = int(os.getenv("GATEWAY_RETRY_MAX_ATTEMPTS", "3"))
GATEWAY_TIMEOUT_SECONDS = int(os.getenv("GATEWAY_TIMEOUT_SECONDS", "10"))

# ── RabbitMQ (logging opcional) ───────────────────────────────────────────────
ENABLE_RABBITMQ_LOGGING = os.getenv("ENABLE_RABBITMQ_LOGGING", "0") == "1"

_logging_handlers: dict = {
    "console": {
        "class": "logging.StreamHandler",
        "formatter": "json",
    }
}

if ENABLE_RABBITMQ_LOGGING:
    _logging_handlers["rabbitmq"] = {
        "level": os.getenv("RABBITMQ_LOG_LEVEL", "INFO"),
        "class": "apps.core.libs.rabbitmq_handler.RabbitMQHandler",
        "host": os.getenv("RABBITMQ_HOST", ""),
        "virtual_host": os.getenv("RABBITMQ_VIRTUAL_HOST", "/"),
        "queue": os.getenv("RABBITMQ_LOG_QUEUE", ""),
        "username": os.getenv("RABBITMQ_USERNAME", ""),
        "password": os.getenv("RABBITMQ_PASSWORD", ""),
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "rename_fields": {
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
        }
    },
    "handlers": _logging_handlers,
    "loggers": {
        "gateway_apps": {
            "handlers": (
                ["console", "rabbitmq"]
                if ENABLE_RABBITMQ_LOGGING
                else ["console"]
            ),
            "level": NIVEL_LOG,
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": NIVEL_LOG,
    },
}

# ── Elastic APM ───────────────────────────────────────────────────────────────
ELASTIC_APM = {
    "SERVICE_NAME": os.getenv("ELASTIC_APM_SERVICE_NAME", NOME_APLICACAO),
    "SECRET_TOKEN": os.getenv("ELASTIC_APM_SECRET_TOKEN", ""),
    "SERVER_URL": os.getenv(
        "ELASTIC_APM_SERVER_URL", "http://localhost:8200"
    ),
    "ENVIRONMENT": os.getenv("ELASTIC_APM_ENVIRONMENT", AMBIENTE_APLICACAO),
    "ENABLED": os.getenv("ELASTIC_APM_ENABLED", "0") == "1",
    "CAPTURE_HEADERS": os.getenv("ELASTIC_APM_CAPTURE_HEADERS", "1") == "1",
    "TRANSACTION_SAMPLE_RATE": float(
        os.getenv("ELASTIC_APM_TRANSACTION_SAMPLE_RATE", "0.3")
    ),
    "METRICS_INTERVAL": os.getenv("ELASTIC_APM_METRICS_INTERVAL", "10s"),
    "FLUSH_INTERVAL": os.getenv("ELASTIC_APM_FLUSH_INTERVAL", "10s"),
    "MAX_BATCH_EVENT_COUNT": int(
        os.getenv("ELASTIC_APM_MAX_BATCH_EVENT_COUNT", "1000")
    ),
    "MAX_QUEUE_EVENT_COUNT": int(
        os.getenv("ELASTIC_APM_MAX_QUEUE_EVENT_COUNT", "1000")
    ),
    "TRANSACTION_MAX_SPANS": int(
        os.getenv("ELASTIC_APM_TRANSACTION_MAX_SPANS", "500")
    ),
    "LOG_LEVEL": os.getenv("ELASTIC_APM_LOG_LEVEL", "INFO"),
}

# ── DRF ───────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.controle_gateway.api.authentication.ApiKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SME-IntegracaoEOL-TransitionGateway API",
    "DESCRIPTION": (
        "Gateway de transição que expõe endpoints compatíveis com o legado EOL "
        "roteando para os novos microsserviços via proxy sidecar."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": API_KEY_HEADER,
            }
        }
    },
    "SECURITY": [{"ApiKeyAuth": []}],
}
