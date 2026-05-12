"""Configuração Django do TransitionGateway."""

import os
from pathlib import Path

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
    "elasticapm.contrib.django",
    "apps.core",
    "apps.pedagogico",
    "apps.professores",
    "apps.institucional",
]

MIDDLEWARE = [
    "elasticapm.contrib.django.middleware.TracingMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "apps.core.middleware.RequestIDMiddleware",
    "apps.core.middleware.LoggingContextMiddleware",
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

GATEWAY_TIMEOUT_SECONDS = int(os.getenv("GATEWAY_TIMEOUT_SECONDS", "10"))

ENABLE_RABBITMQ_LOGGING = os.getenv("ENABLE_RABBITMQ_LOGGING", "0") == "1"

_logging_handlers: dict = {
    "console": {
        "class": "logging.StreamHandler",
        "formatter": "json",
        "filters": ["context"],
    },
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
        "filters": ["context"],
    }

_active_handlers = ["console"] + (
    ["rabbitmq"] if ENABLE_RABBITMQ_LOGGING else []
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "context": {"()": "apps.core.logging_context.ContextFilter"},
    },
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": (
                "%(asctime)s %(levelname)s %(name)s %(message)s"
                " %(request_id)s %(service)s"
                " %(transaction_id)s %(trace_id)s"
            ),
            "rename_fields": {
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
        },
    },
    "handlers": _logging_handlers,
    "root": {"handlers": _active_handlers, "level": "INFO"},
    "loggers": {
        "django": {
            "handlers": _active_handlers,
            "level": "WARNING",
            "propagate": False,
        },
        "elasticapm": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "pika": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

ELASTIC_APM = {
    "SERVICE_NAME": os.getenv(
        "ELASTIC_APM_SERVICE_NAME", "transition-gateway"
    ),
    "SERVER_URL": os.getenv("ELASTIC_APM_SERVER_URL", "http://localhost:8200"),
    "SECRET_TOKEN": os.getenv("ELASTIC_APM_SECRET_TOKEN", ""),
    "ENVIRONMENT": os.getenv("ELASTIC_APM_ENVIRONMENT", "local"),
    "ENABLED": os.getenv("ELASTIC_APM_ENABLED", "1") == "1",
    "DEBUG": os.getenv("ELASTIC_APM_DEBUG", "1" if DEBUG else "0") == "1",
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
